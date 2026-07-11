import os
import io
import time
import logging
import subprocess
import tempfile
import glob

from google import genai
from google.genai import types

logger = logging.getLogger("captionforge.caption_generator")

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
}

CAPTION_PROMPT = (
    "These are evenly-spaced frames extracted from a video. Study them carefully in order.\n\n"
    "Write a detailed, factual description of exactly what happens:\n"
    "- WHO is in the video (people, animals, specific objects)\n"
    "- WHAT specific actions occur — be precise, not vague\n"
    "- WHERE it takes place (environment, setting, background)\n"
    "- HOW events change across the frames (sequence of actions)\n"
    "- Any notable objects, text on screen, or significant details\n\n"
    "Write 3-4 rich, concrete sentences about the ACTUAL content you see. "
    "Never say 'a sequence of events' or 'an entity'. Be specific.\n\n"
    "Output ONLY the factual description. No headers, bullets, or reasoning."
)


class CaptionGenerator:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def generate_base_caption(self, video_path: str) -> str:
        if not self.client:
            raise Exception(
                "No GEMINI_API_KEY configured. Add it to Vercel → Settings → Environment Variables."
            )

        # Strategy 1: Gemini File API (handles large files, native video understanding)
        try:
            return self._gemini_file_api(video_path)
        except Exception as e:
            logger.warning(f"[File API] Failed: {e}. Falling back to frame extraction...")

        # Strategy 2: Extract frames with imageio-ffmpeg → send as images to Gemini
        try:
            return self._frames_via_imageio_ffmpeg(video_path)
        except Exception as e2:
            logger.error(f"[Frames] Failed: {e2}")
            raise Exception(
                f"Could not process video. File API error + Frame extraction failed. "
                f"Try uploading an MP4 (H.264) video under 50MB. Detail: {e2}"
            )

    # ------------------------------------------------------------------ #
    #  Strategy 1 — Gemini File API                                        #
    # ------------------------------------------------------------------ #
    def _gemini_file_api(self, video_path: str) -> str:
        ext = os.path.splitext(video_path)[1].lower()
        mime_type = MIME_MAP.get(ext, "video/mp4")

        logger.info(f"[File API] Uploading as {mime_type}: {os.path.basename(video_path)}")

        video_file = self.client.files.upload(
            file=video_path,
            config=types.UploadFileConfig(
                mime_type=mime_type,
                display_name="captionforge_video"
            )
        )

        max_wait = 180
        waited = 0
        while video_file.state.name == "PROCESSING":
            if waited >= max_wait:
                raise Exception(f"File API timed out after {max_wait}s.")
            time.sleep(4)
            waited += 4
            video_file = self.client.files.get(name=video_file.name)
            logger.info(f"  [{waited}s] state={video_file.state.name}")

        if video_file.state.name == "FAILED":
            try:
                self.client.files.delete(name=video_file.name)
            except Exception:
                pass
            raise Exception(f"Gemini rejected this video format ({mime_type}). Will try frame extraction.")

        prompt = (
            "Watch this entire video carefully from start to finish.\n\n"
            "Write a detailed, factual description:\n"
            "- WHO is in the video (people, animals, objects)\n"
            "- WHAT specific actions occur\n"
            "- WHERE it takes place\n"
            "- HOW events unfold over time\n"
            "- Any notable text, dialogue, or sounds\n\n"
            "Write 3-4 rich, concrete sentences. Never use vague terms like 'a sequence of events'. "
            "Be specific about the actual content.\n\n"
            "Output ONLY the factual description. No headers, bullets, or reasoning."
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_file, prompt],
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=600),
        )
        try:
            self.client.files.delete(name=video_file.name)
        except Exception:
            pass

        caption = response.text.strip()
        logger.info(f"[File API] Caption: {caption[:80]}...")
        return caption

    # ------------------------------------------------------------------ #
    #  Strategy 2 — imageio-ffmpeg frame extraction (static FFmpeg binary) #
    # ------------------------------------------------------------------ #
    def _frames_via_imageio_ffmpeg(self, video_path: str) -> str:
        """
        Uses imageio-ffmpeg (which bundles a static FFmpeg binary in the pip wheel)
        to extract frames as JPEG, then sends them as inline images to Gemini.
        Works on Vercel without any system-level ffmpeg installed.
        """
        import imageio_ffmpeg
        from PIL import Image as PILImage

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        logger.info(f"[Frames] ffmpeg found: {ffmpeg_exe}")

        image_parts = []

        with tempfile.TemporaryDirectory(dir="/tmp") as tmpdir:
            out_pattern = os.path.join(tmpdir, "frame_%03d.jpg")

            # Try to get 8 evenly-spaced frames using fps filter
            # First probe the video duration
            probe_cmd = [
                ffmpeg_exe, "-i", video_path,
                "-f", "null", "-"
            ]
            probe = subprocess.run(probe_cmd, capture_output=True, timeout=30, text=True)
            
            # Try with select filter for even distribution
            cmd = [
                ffmpeg_exe, "-i", video_path,
                "-vf", "select='not(mod(n,30))',scale=640:360",
                "-vsync", "vfr",
                "-frames:v", "8",
                "-q:v", "3",
                out_pattern,
                "-y", "-loglevel", "error"
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=90)

            # Fallback: just grab first 8 frames at 1fps
            if result.returncode != 0 or not glob.glob(os.path.join(tmpdir, "frame_*.jpg")):
                cmd2 = [
                    ffmpeg_exe, "-i", video_path,
                    "-vf", "fps=1,scale=640:360",
                    "-frames:v", "8",
                    out_pattern,
                    "-y", "-loglevel", "error"
                ]
                subprocess.run(cmd2, capture_output=True, timeout=90)

            for fpath in sorted(glob.glob(os.path.join(tmpdir, "frame_*.jpg")))[:8]:
                with open(fpath, "rb") as fp:
                    image_parts.append(
                        types.Part.from_bytes(data=fp.read(), mime_type="image/jpeg")
                    )

        if not image_parts:
            raise Exception("imageio-ffmpeg could not extract any frames from this video.")

        logger.info(f"[Frames] Extracted {len(image_parts)} frames. Sending to Gemini...")
        contents = image_parts + [CAPTION_PROMPT]
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=600),
        )
        caption = response.text.strip()
        logger.info(f"[Frames] Caption: {caption[:80]}...")
        return caption
