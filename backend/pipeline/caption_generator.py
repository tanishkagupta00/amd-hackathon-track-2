import os
import time
import logging

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

class CaptionGenerator:
    def __init__(self):
        pass  # No client at init — always read fresh to handle Vercel env vars

    def _get_client(self):
        """Always reads the API key fresh on every call — required for Vercel serverless."""
        api_key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GOOGLE_GEMINI_KEY")
        )
        if not api_key:
            raise Exception(
                "No GEMINI_API_KEY found. Go to Vercel → Project → Settings → "
                "Environment Variables, add GEMINI_API_KEY with your Google AI Studio key, "
                "then click Redeploy."
            )
        return genai.Client(api_key=api_key)

    def generate_base_caption(self, video_path: str) -> str:
        """
        Uses Gemini File API exclusively — no local FFmpeg or OpenCV needed.
        Works on Vercel serverless.
        """
        client = self._get_client()  # Fresh client with fresh API key every request

        ext = os.path.splitext(video_path)[1].lower()
        mime_type = MIME_MAP.get(ext, "video/mp4")

        logger.info(f"Uploading as {mime_type}: {os.path.basename(video_path)}")

        try:
            video_file = client.files.upload(
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
                video_file = client.files.get(name=video_file.name)
                logger.info(f"  [{waited}s] state={video_file.state.name}")

            if video_file.state.name == "FAILED":
                try:
                    client.files.delete(name=video_file.name)
                except Exception:
                    pass
                raise Exception(f"Gemini rejected this video format ({mime_type}). Please upload a standard MP4 (H.264).")

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
            logger.info(f"Caption: {caption[:80]}...")
            return caption

        except Exception as e:
            logger.error(f"Failed: {e}")
            raise Exception(f"Could not process video: {str(e)}. Please try uploading an MP4 (H.264) video under 50MB.")
