import os
import uuid
import shutil
import logging
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from database import get_db, VideoRecord
from core.config import settings
from schemas.models import (
    VideoUploadResponse,
    VideoUrlUploadRequest,
    CaptionGenerationRequest,
    CaptionResult,
    StyleItem,
    EvaluationRequest,
    EvaluationResponse
)
import requests
from pipeline.pipeline import CaptionForgePipeline
from pipeline.caption_critic import CaptionCritic

router = APIRouter()
logger = logging.getLogger("captionforge.routes")
pipeline = CaptionForgePipeline()
critic = CaptionCritic()

@router.post("/videos", response_model=VideoUploadResponse)
def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Accept any extension — caption_generator will re-encode if Gemini rejects it
    ext = os.path.splitext(file.filename)[1].lower()
    if not ext:
        ext = ".mp4"  # fallback if no extension provided

    video_id = str(uuid.uuid4())
    filename = f"{video_id}{ext}"
    dest_path = os.path.join(settings.STORAGE_DIR, filename)

    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    # Create DB record
    record = VideoRecord(
        id=video_id,
        filename=file.filename,
        status="uploaded"
    )
    record.append_log(f"Video uploaded successfully. Saved locally to storage.")
    db.add(record)
    db.commit()

    return VideoUploadResponse(
        video_id=video_id,
        status="uploaded",
        filename=file.filename
    )

@router.post("/videos/url", response_model=VideoUploadResponse)
def upload_video_from_url(req: VideoUrlUploadRequest, db: Session = Depends(get_db)):
    # Accept any extension — caption_generator will re-encode if Gemini rejects it
    ext = os.path.splitext(req.filename)[1].lower()
    if not ext:
        ext = ".mp4"

    video_id = str(uuid.uuid4())
    filename = f"{video_id}{ext}"
    dest_path = os.path.join(settings.STORAGE_DIR, filename)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; CaptionForge/1.0)",
        "Accept": "*/*",
    }
    last_error = None
    for attempt in range(3):  # 3 attempts for flaky hosts like tmpfiles.org
        try:
            with requests.get(req.url, stream=True, timeout=90, headers=headers, allow_redirects=True) as r:
                r.raise_for_status()

                # Guard: reject HTML error pages served as 200 OK (common with tmpfiles.org)
                content_type = r.headers.get("Content-Type", "")
                if "text/html" in content_type:
                    raise Exception(
                        f"tmpfiles.org returned an HTML page instead of the video file. "
                        f"The temporary link may have expired. Please re-upload the video."
                    )

                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)

            # Guard: verify we wrote a real video, not a 0-byte or tiny HTML blob
            downloaded_size = os.path.getsize(dest_path)
            logger.info(f"Downloaded video size: {downloaded_size / 1024:.1f} KB  path={dest_path}")
            if downloaded_size < 10_000:  # less than 10 KB is definitely not a real video
                os.remove(dest_path)
                raise Exception(
                    f"Downloaded file is only {downloaded_size} bytes — "
                    f"the temporary link likely expired or returned an error page. "
                    f"Please re-upload the video."
                )

            last_error = None
            break  # success
        except Exception as e:
            last_error = e
            logger.warning(f"Download attempt {attempt+1}/3 failed: {e}")
            if attempt < 2:
                import time; time.sleep(2)
    if last_error:
        raise HTTPException(status_code=500, detail=f"Failed to download video from URL after 3 attempts: {str(last_error)}")

    # Create DB record
    record = VideoRecord(
        id=video_id,
        filename=req.filename,
        status="uploaded"
    )
    record.append_log("Video downloaded from URL successfully.")
    db.add(record)
    db.commit()

    return VideoUploadResponse(
        video_id=video_id,
        status="uploaded",
        filename=req.filename
    )

@router.get("/videos/{id}")
def get_video_status(id: str, db: Session = Depends(get_db)):
    record = db.query(VideoRecord).filter(VideoRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Video record not found.")

    return {
        "video_id": record.id,
        "filename": record.filename,
        "status": record.status,
        "logs": record.logs.split("\n") if record.logs else [],
        "created_at": record.created_at
    }

def run_pipeline_job(video_id: str, video_path: str, db_session_factory):
    # Isolated db transaction
    db = db_session_factory()
    try:
        record = db.query(VideoRecord).filter(VideoRecord.id == video_id).first()
        if not record:
            return

        def on_progress(stage: str, msg: str):
            record.status = stage
            record.append_log(msg)
            db.commit()

        # Run pipeline
        res = pipeline.process_video(video_path, progress_callback=on_progress)
        
        record.status = "completed"
        record.set_captions(res["captions"])
        record.set_evaluations(res["evaluations"])
        record.append_log("Captioning pipeline finished successfully.")
        db.commit()
    except Exception as e:
        record.status = "failed"
        record.append_log(f"CRITICAL ERROR in pipeline execution: {str(e)}")
        db.commit()
    finally:
        db.close()

@router.post("/captions/generate", response_model=CaptionResult)
def generate_captions(
    req: CaptionGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Self-contained caption generation for Vercel serverless.

    New flow (Vercel):
      - Frontend uploads to tmpfiles.org, gets a directUrl
      - Frontend calls this endpoint with { video_id, video_url }
      - This endpoint downloads the video fresh from video_url, runs the pipeline,
        returns captions — no DB lookup, no /videos/url call needed at all.

    Legacy flow (local / Railway):
      - Frontend called /videos/url first, which saved file + DB record
      - This endpoint finds the record by video_id and uses the saved file
    """
    import tempfile, shutil as _shutil

    tmp_dir = None

    try:
        logger.info(
            "[/captions/generate] request=%s has_video_url=%s client_host=%s",
            req.video_id,
            bool(req.video_url),
            getattr(req, "client_host", None),
        )
        if req.video_url:
            logger.info(f"[generate] Self-contained mode — downloading from URL: {req.video_url[:80]}")

            tmp_dir = tempfile.mkdtemp(prefix="captionforge_gen_")
            url_path = req.video_url.split("?")[0]
            ext = os.path.splitext(url_path)[1].lower() or ".mp4"
            video_path = os.path.join(tmp_dir, f"video{ext}")

            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; CaptionForge/1.0)",
                "Accept": "*/*",
            }
            last_error = None
            for attempt in range(3):
                try:
                    with requests.get(
                        req.video_url, stream=True, timeout=120,
                        headers=headers, allow_redirects=True
                    ) as r:
                        r.raise_for_status()
                        content_type = r.headers.get("Content-Type", "")
                        if "text/html" in content_type:
                            raise Exception(
                                "The video URL returned an HTML page — the tmpfiles.org "
                                "link likely expired. Please re-upload the video."
                            )
                        with open(video_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=65536):
                                if chunk:
                                    f.write(chunk)

                    file_size = os.path.getsize(video_path)
                    logger.info(f"[generate] Downloaded {file_size / 1024:.1f} KB → {video_path}")
                    if file_size < 10_000:
                        raise Exception(
                            f"Downloaded file is only {file_size} bytes — "
                            "link expired or returned an error page. Please re-upload."
                        )
                    last_error = None
                    break  # success
                except Exception as e:
                    last_error = e
                    logger.warning(f"[generate] Download attempt {attempt + 1}/3 failed: {e}")
                    if attempt < 2:
                        import time; time.sleep(3)

            if last_error:
                raise HTTPException(
                    status_code=400,
                    detail=str(last_error)
                )

            try:
                res = pipeline.process_video(video_path)
                return CaptionResult(
                    status="completed",
                    video_id=req.video_id,
                    base_caption=res.get("base_caption"),
                    captions={
                        k: StyleItem(style=k, caption=v)
                        for k, v in (res.get("captions") or {}).items()
                        if isinstance(k, str)
                    },
                    evaluations=res.get("evaluations") or {},
                )
            except HTTPException:
                raise
            except Exception as e:
                logger.exception("[/captions/generate] pipeline failed")
                raise HTTPException(status_code=500, detail=str(e))

        # ── Path B: no video_url — legacy DB lookup (local / persistent server) ─
        record = db.query(VideoRecord).filter(VideoRecord.id == req.video_id).first()
        if not record:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Video record not found and no video_url was provided. "
                    "The frontend must include video_url in the request body."
                )
            )

        ext = os.path.splitext(record.filename)[1]
        video_path = os.path.join(settings.STORAGE_DIR, f"{req.video_id}{ext}")
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video source file missing from storage.")

        record.status = "queued"
        record.logs = ""
        record.append_log("Started video processing task.")
        db.commit()

        from database import SessionLocal
        run_pipeline_job(req.video_id, video_path, SessionLocal)

        db.refresh(record)
        if record.status == "failed":
            raise HTTPException(status_code=500, detail=record.logs)

        return {
            "status": "completed",
            "video_id": req.video_id,
            "captions": record.get_captions(),
            "evaluations": record.get_evaluations(),
        }

    finally:
        if tmp_dir:
            _shutil.rmtree(tmp_dir, ignore_errors=True)

@router.get("/captions/{id}")
def get_captions(id: str, db: Session = Depends(get_db)):
    record = db.query(VideoRecord).filter(VideoRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Video record not found.")

    if record.status != "completed":
        raise HTTPException(status_code=400, detail=f"Captions are not ready. Status: {record.status}")

    return {
        "video_id": record.id,
        "captions": record.get_captions(),
        "evaluations": record.get_evaluations()
    }

@router.post("/evaluations", response_model=EvaluationResponse)
def evaluate_caption(req: EvaluationRequest):
    res = critic.evaluate_caption(req.caption, req.style, req.entities)
    return EvaluationResponse(
        caption=res["caption"],
        accuracy_score=res["accuracy_score"],
        style_score=res["style_score"],
        hallucination_detected=res["hallucination_detected"],
        hallucinated_words=res["hallucinated_words"]
    )

@router.get("/health")
def health_check():
    return {"status": "healthy", "version": settings.VERSION}

@router.get("/config")
def get_config():
    return {
        "project_name": settings.PROJECT_NAME,
        "storage_dir": settings.STORAGE_DIR,
        "database": "SQLite",
        "primary_vlm": "Qwen2.5-VL (Mock/API)",
        "stylist_model": "Llama-3.3 (Mock/API)"
    }
