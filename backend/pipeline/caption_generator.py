import os
import time
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("captionforge.caption_generator")


class CaptionGenerator:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_base_caption(self, video_path: str) -> str:
        """
        Creates a factual, non-stylized base caption by uploading the video to
        Gemini's File API and having it watch the entire video.
        NO OpenCV dependency - uses only the Gemini File API.
        """
        if not self.client:
            logger.error("No Gemini API key configured. Cannot generate caption without GEMINI_API_KEY.")
            return (
                "A video was uploaded but could not be analyzed because no GEMINI_API_KEY "
                "is configured. Please add the GEMINI_API_KEY environment variable."
            )

        return self._gemini_caption(video_path)

    def _gemini_caption(self, video_path: str) -> str:
        """Upload video to Gemini File API and generate a detailed factual caption."""
        logger.info(f"Uploading video to Gemini File API: {video_path}")

        video_file = self.client.files.upload(file=video_path)
        logger.info(f"Video uploaded. State: {video_file.state.name}. Waiting for processing...")

        # Poll until Gemini finishes processing the video (max 3 minutes)
        max_wait = 180
        waited = 0
        while video_file.state.name == "PROCESSING":
            if waited >= max_wait:
                raise Exception(f"Gemini file processing timed out after {max_wait}s.")
            time.sleep(4)
            waited += 4
            video_file = self.client.files.get(name=video_file.name)
            logger.info(f"Waited {waited}s... state: {video_file.state.name}")

        if video_file.state.name == "FAILED":
            raise Exception("Gemini File API returned FAILED state for this video.")

        logger.info("Gemini finished processing video. Generating factual base caption...")

        prompt = (
            "Watch this entire video carefully from start to finish.\n\n"
            "Write a detailed, factual description of exactly what happens:\n"
            "- WHO is in the video (people, animals, specific objects)\n"
            "- WHAT specific actions occur (not vague — be precise)\n"
            "- WHERE it takes place (environment, setting, background)\n"
            "- HOW events unfold over time (sequence, any changes)\n"
            "- Any notable objects, text on screen, dialogue, or sounds\n\n"
            "Write 3-4 rich, concrete sentences. "
            "Do NOT say vague things like 'a sequence of events' or 'an entity interacts'. "
            "Be specific about what you actually see happening.\n\n"
            "Output ONLY the factual description. No headers, no bullets, no reasoning."
        )

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[video_file, prompt],
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=600
            )
        )

        # Clean up the uploaded file from Gemini storage
        try:
            self.client.files.delete(name=video_file.name)
        except Exception:
            pass

        caption = response.text.strip()
        logger.info(f"Base caption generated: {caption[:120]}...")
        return caption
