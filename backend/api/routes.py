import os
import uuid
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import get_db, VideoRecord
from core.config import settings
from schemas.models import (
    VideoUploadResponse,
    CaptionGenerationRequest,
    EvaluationRequest,
    EvaluationResponse
)
from pipeline.pipeline import CaptionForgePipeline
from pipeline.caption_critic import CaptionCritic

router = APIRouter()
pipeline = CaptionForgePipeline()
critic = CaptionCritic()

@router.post("/videos", response_model=VideoUploadResponse)
def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".mp4", ".mov", ".avi"]:
        raise HTTPException(status_code=400, detail="Unsupported video format. Must be MP4, MOV, or AVI.")

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

@router.post("/captions/generate")
def generate_captions(
    req: CaptionGenerationRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    record = db.query(VideoRecord).filter(VideoRecord.id == req.video_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Video record not found.")

    ext = os.path.splitext(record.filename)[1]
    video_path = os.path.join(settings.STORAGE_DIR, f"{req.video_id}{ext}")

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video source file missing from storage.")

    record.status = "queued"
    record.logs = ""
    record.append_log("Started video processing task.")
    db.commit()

    # Synchronous execution for Vercel Serverless Function compatibility
    from database import SessionLocal
    run_pipeline_job(req.video_id, video_path, SessionLocal)

    return {"status": "completed", "video_id": req.video_id}

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
