import os
import time
import logging
import mimetypes
from google import genai
from google.genai import types

logger = logging.getLogger("captionforge.caption_generator")

SUPPORTED_VIDEO_MIMES = {
    ".mp4":  "video/mp4",
    ".mov":  "video/quicktime",
    ".avi":  "video/x-msvideo",
    ".webm": "video/webm",
    ".mkv":  "video/x-matroska",
    ".flv":  "video/x-flv",
    ".wmv":  "video/x-ms-wmv",
}

CAPTION_PROMPT = (
    "Watch this entire video carefully from start to finish.\n\n"
    "Write a detailed, factual description of exactly what happens:\n"
    "- WHO is in the video (people, animals, specific objects)\n"
    "- WHAT specific actions occur — be precise, not vague\n"
    "- WHERE it takes place (environment, setting, background details)\n"
    "- HOW events unfold and change over time\n"
    "- Any notable objects, text on screen, dialogue, or sounds\n\n"
    "Write 3-4 rich, concrete sentences. "
    "Do NOT be generic — never say 'a sequence of events' or 'an entity'. "
    "Describe the real, specific content you see.\n\n"
    "Output ONLY the factual description paragraph. No headers, bullets, or reasoning."
)


class CaptionGenerator:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_base_caption(self, video_path: str) -> str:
        """
        Generates a detailed factual base caption by having Gemini watch the video.
        Strategy:
          1. Try Gemini File API (best quality, handles large files)
          2. If File API fails (unsupported codec / FAILED state), try inline bytes upload
          3. If both fail, raise so the pipeline logs the real error
        """
        if not self.client:
            raise Exception(
                "No GEMINI_API_KEY configured. Please add it to your Vercel environment variables."
            )

        # --- Strategy 1: Gemini File API ---
        try:
            return self._caption_via_file_api(video_path)
        except Exception as e:
            logger.warning(f"File API strategy failed: {e}. Trying inline bytes...")

        # --- Strategy 2: Inline bytes (works for videos < ~20MB) ---
        try:
            return self._caption_via_inline_bytes(video_path)
        except Exception as e2:
            logger.error(f"Inline bytes strategy also failed: {e2}")
            raise Exception(
                f"Gemini could not process this video. "
                f"File API error: try a different video format (MP4 H.264 recommended). "
                f"Detail: {e2}"
            )

    # ------------------------------------------------------------------ #
    #  Strategy 1 — Gemini File API                                        #
    # ------------------------------------------------------------------ #
    def _caption_via_file_api(self, video_path: str) -> str:
        logger.info(f"[File API] Uploading: {video_path}")
        video_file = self.client.files.upload(file=video_path)

        # Poll until Gemini finishes transcoding / processing
        max_wait = 180
        waited = 0
        while video_file.state.name == "PROCESSING":
            if waited >= max_wait:
                raise Exception(f"File API timed out after {max_wait}s.")
            time.sleep(4)
            waited += 4
            video_file = self.client.files.get(name=video_file.name)
            logger.info(f"  [{waited}s] state: {video_file.state.name}")

        if video_file.state.name == "FAILED":
            # Clean up before raising
            try:
                self.client.files.delete(name=video_file.name)
            except Exception:
                pass
            raise Exception("Gemini File API returned FAILED state — video format may be unsupported.")

        logger.info("File API ready. Generating caption...")
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_file, CAPTION_PROMPT],
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=600,
            ),
        )

        # Clean up
        try:
            self.client.files.delete(name=video_file.name)
        except Exception:
            pass

        caption = response.text.strip()
        logger.info(f"[File API] Caption: {caption[:100]}...")
        return caption

    # ------------------------------------------------------------------ #
    #  Strategy 2 — Inline bytes (no transcoding wait, < ~20 MB)          #
    # ------------------------------------------------------------------ #
    def _caption_via_inline_bytes(self, video_path: str) -> str:
        ext = os.path.splitext(video_path)[1].lower()
        mime_type = SUPPORTED_VIDEO_MIMES.get(ext, "video/mp4")

        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        logger.info(f"[Inline] Reading {file_size_mb:.1f} MB video as {mime_type}...")

        if file_size_mb > 19:
            raise Exception(
                f"Video is {file_size_mb:.1f} MB — too large for inline upload (max ~19 MB). "
                "Please upload a shorter/smaller video."
            )

        with open(video_path, "rb") as f:
            video_bytes = f.read()

        video_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)

        logger.info("[Inline] Sending bytes to Gemini...")
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_part, CAPTION_PROMPT],
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=600,
            ),
        )

        caption = response.text.strip()
        logger.info(f"[Inline] Caption: {caption[:100]}...")
        return caption
