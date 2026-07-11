import io
import os
import time
import shutil
import logging
import tempfile
import subprocess

from google import genai
from google.genai import types

logger = logging.getLogger("captionforge.caption_generator")

# Every MIME type the Gemini File API natively accepts
MIME_MAP = {
    ".mp4":  "video/mp4",
    ".mov":  "video/quicktime",
    ".avi":  "video/x-msvideo",
    ".webm": "video/webm",
    ".mkv":  "video/x-matroska",
    ".flv":  "video/x-flv",
    ".wmv":  "video/x-ms-wmv",
    ".3gp":  "video/3gpp",
    ".mpg":  "video/mpeg",
    ".mpeg": "video/mpeg",
    ".m4v":  "video/mp4",
    ".ts":   "video/mp2t",
    ".mts":  "video/mp2t",
    ".m2ts": "video/mp2t",
    ".ogv":  "video/ogg",
    ".rm":   "video/x-realmedia",
    ".rmvb": "video/x-realmedia",
    ".divx": "video/x-msvideo",
    ".f4v":  "video/x-flv",
    ".asf":  "video/x-ms-asf",
    ".vob":  "video/mpeg",
}

# Formats that Gemini natively handles reliably without re-encoding
GEMINI_NATIVE = {".mp4", ".mov", ".avi", ".webm", ".3gp", ".mpg", ".mpeg", ".m4v"}


def _get_ffmpeg_binary() -> str | None:
    """
    Returns the path to an ffmpeg binary, trying three sources in order:
    1. imageio-ffmpeg bundled static binary (always available if installed)
    2. ffmpeg on system PATH
    3. None — conversion not available
    """
    # 1. imageio-ffmpeg bundled binary
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path and os.path.exists(path):
            logger.info(f"Using imageio-ffmpeg binary: {path}")
            return path
    except Exception:
        pass

    # 2. System PATH
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, timeout=5
        )
        if result.returncode == 0:
            logger.info("Using system ffmpeg from PATH.")
            return "ffmpeg"
    except Exception:
        pass

    logger.warning("No ffmpeg binary found — format conversion unavailable.")
    return None


def _convert_to_h264_mp4(input_path: str, ffmpeg_bin: str) -> str:
    """
    Re-encodes input_path to H.264 MP4 using ffmpeg.
    Returns the path to the converted file (in a temp dir).
    Raises on failure.
    """
    tmp_dir = tempfile.mkdtemp(prefix="captionforge_conv_")
    output_path = os.path.join(tmp_dir, "converted.mp4")

    cmd = [
        ffmpeg_bin,
        "-y",                       # overwrite without asking
        "-i", input_path,           # input
        "-c:v", "libx264",          # H.264 video codec
        "-preset", "ultrafast",     # fastest encode — quality doesn't matter here
        "-crf", "23",               # reasonable quality
        "-c:a", "aac",              # AAC audio
        "-movflags", "+faststart",  # web-optimised
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",  # ensure even dimensions
        output_path
    ]

    logger.info(f"Re-encoding to H.264 MP4: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, timeout=120)

    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace")[-500:]
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise Exception(f"ffmpeg conversion failed: {stderr}")

    converted_size = os.path.getsize(output_path)
    logger.info(f"Conversion complete: {converted_size / 1024 / 1024:.2f} MB → {output_path}")
    return output_path


def _upload_and_wait(client, video_path: str, mime_type: str, display_name: str):
    """
    Uploads video_path to the Gemini File API and polls until ACTIVE or FAILED.
    Returns the File object when ACTIVE.
    Raises on FAILED or timeout.
    """
    file_size = os.path.getsize(video_path)
    BYTESIO_THRESHOLD = 20 * 1024 * 1024  # 20 MB

    if file_size <= BYTESIO_THRESHOLD:
        with open(video_path, "rb") as f:
            upload_source = io.BytesIO(f.read())
        logger.info(f"BytesIO upload path ({file_size / 1024 / 1024:.2f} MB).")
    else:
        upload_source = open(video_path, "rb")
        logger.info(f"Streaming upload path ({file_size / 1024 / 1024:.2f} MB).")

    try:
        video_file = client.files.upload(
            file=upload_source,
            config=types.UploadFileConfig(
                mime_type=mime_type,
                display_name=display_name,
            )
        )
    finally:
        if not isinstance(upload_source, io.BytesIO):
            upload_source.close()

    # Poll until not PROCESSING
    max_wait = 180
    waited = 0
    while video_file.state.name == "PROCESSING":
        if waited >= max_wait:
            raise Exception(f"Gemini File API timed out after {max_wait}s.")
        time.sleep(4)
        waited += 4
        video_file = client.files.get(name=video_file.name)
        logger.info(f"  [{waited}s] state={video_file.state.name}")

    if video_file.state.name == "FAILED":
        try:
            client.files.delete(name=video_file.name)
        except Exception:
            pass
        raise Exception(
                f"Gemini File API processing failed for `{display_name}` after waiting "
                f"{max_wait}s. Check file format/size and retry."
            )

    return video_file


class CaptionGenerator:
    def __init__(self):
        pass  # No client at init — always read fresh for Vercel serverless

    def _get_client(self):
        """Reads API key fresh on every call — required for Vercel serverless env vars."""
        api_key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GOOGLE_GEMINI_KEY")
        )
        if not api_key:
            raise Exception(
                "No GEMINI_API_KEY found. Go to Vercel → Project → Settings → "
                "Environment Variables, add GEMINI_API_KEY, then Redeploy."
            )
        return genai.Client(api_key=api_key)

    def generate_base_caption(self, video_path: str) -> str:
        """
        Accepts ANY video format.

        Strategy:
        1. Try uploading the original file directly to Gemini.
        2. If Gemini returns FAILED (unsupported codec / container):
           a. Locate an ffmpeg binary (imageio-ffmpeg bundled or system PATH).
           b. Re-encode to H.264 MP4 and retry the upload.
        3. If ffmpeg is not available, raise a helpful error.
        """
        client = self._get_client()

        ext = os.path.splitext(video_path)[1].lower()
        mime_type = MIME_MAP.get(ext, "video/mp4")
        display_name = f"captionforge_video{ext}"

        # ── File integrity guard ───────────────────────────────────────────────
        file_size = os.path.getsize(video_path)
        file_size_mb = file_size / (1024 * 1024)
        logger.info(f"Processing: {os.path.basename(video_path)} | {file_size_mb:.2f} MB | mime={mime_type}")

        if file_size < 10_000:
            raise Exception(
                f"Video file is only {file_size} bytes — the download link likely "
                f"expired before the server fetched it. Please re-upload the file."
            )

        # ── Attempt 1: upload original ─────────────────────────────────────────
        converted_tmp_dir = None
        active_path  = video_path
        active_mime  = mime_type
        active_name  = display_name

        try:
            try:
                logger.info("Attempt 1: uploading original file to Gemini.")
                video_file = _upload_and_wait(client, active_path, active_mime, active_name)

            except Exception as e:
                if "FAILED" not in str(e):
                    raise  # something else went wrong — propagate immediately

                # ── Attempt 2: re-encode to H.264 MP4 then retry ──────────────
                logger.warning(
                    f"Gemini rejected original format ({ext}). "
                    "Attempting automatic re-encode to H.264 MP4..."
                )

                ffmpeg_bin = _get_ffmpeg_binary()
                if not ffmpeg_bin:
                    raise Exception(
                        f"Gemini does not support the '{ext}' format and ffmpeg is not "
                        f"available on this server to convert it. "
                        f"Please re-encode your video to H.264 MP4 before uploading."
                    )

                converted_path = _convert_to_h264_mp4(video_path, ffmpeg_bin)
                converted_tmp_dir = os.path.dirname(converted_path)

                logger.info("Attempt 2: uploading re-encoded H.264 MP4 to Gemini.")
                video_file = _upload_and_wait(
                    client,
                    converted_path,
                    "video/mp4",
                    "captionforge_video_converted.mp4",
                )

            # ── Generate caption ───────────────────────────────────────────────
            prompt = (
                "Watch this entire video carefully from start to finish.\n\n"
                "Write a detailed, factual description:\n"
                "- WHO is in the video (people, animals, objects)\n"
                "- WHAT specific actions occur\n"
                "- WHERE it takes place\n"
                "- HOW events unfold over time\n"
                "- Any notable text, dialogue, or sounds\n\n"
                "Write 3-4 rich, concrete sentences. "
                "Never use vague terms like 'a sequence of events'. "
                "Be specific about the actual content.\n\n"
                "Output ONLY the factual description. No headers, bullets, or reasoning."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[video_file, prompt],
                config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=600),
            )

            try:
                client.files.delete(name=video_file.name)
            except Exception:
                pass

            caption = response.text.strip()
            logger.info(f"Caption generated: {caption[:80]}...")
            return caption

        except Exception as e:
            logger.error(f"Caption generation failed: {e}")
            raise Exception(
                f"Could not process video: {str(e)}"
            )
        finally:
            # Clean up any temporary converted file
            if converted_tmp_dir:
                shutil.rmtree(converted_tmp_dir, ignore_errors=True)
