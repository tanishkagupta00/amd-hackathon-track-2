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
        Creates a factual, non-stylized base caption by watching the real video via Gemini.
        Uploads the video file to the Gemini File API, waits for processing,
        then sends it with a detailed analysis prompt.
        Falls back to Fireworks Llama Vision if Gemini is unavailable.
        """
        if self.client:
            return self._gemini_caption(video_path)
        else:
            logger.warning("No Gemini API key found. Falling back to Fireworks Vision.")
            return self._fireworks_vision_caption(video_path)

    def _gemini_caption(self, video_path: str) -> str:
        """Upload video to Gemini File API and generate a detailed factual caption."""
        try:
            logger.info(f"Uploading video to Gemini File API: {video_path}")
            video_file = self.client.files.upload(file=video_path)

            # Poll until Gemini finishes processing the video
            max_wait = 120  # seconds
            waited = 0
            while video_file.state.name == "PROCESSING":
                if waited >= max_wait:
                    raise Exception(f"Gemini file processing timed out after {max_wait}s.")
                time.sleep(3)
                waited += 3
                video_file = self.client.files.get(name=video_file.name)

            if video_file.state.name == "FAILED":
                raise Exception("Gemini File API returned FAILED state for this video.")

            logger.info("Gemini finished processing. Generating factual caption...")

            prompt = """Watch this entire video very carefully from start to finish.

Your task: Write a detailed, factual, scene-by-scene description of exactly what happens in this video.

Describe:
- WHO is in the video (people, animals, objects as main subjects)
- WHAT they are doing (specific actions, movements, interactions)
- WHERE it is set (environment, location, background details)
- HOW things change over time (sequence of events, any transitions)
- Any notable objects, text, dialogue, or sounds visible

Write 3-4 rich, specific sentences. Be precise and concrete about actual events in the video.
Do NOT be vague or generic. Do NOT say "a sequence of events" or "an entity".
Output ONLY the factual description paragraph. No headers, no bullets, no reasoning."""

            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[video_file, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=600
                )
            )

            # Clean up uploaded file
            try:
                self.client.files.delete(name=video_file.name)
            except Exception:
                pass

            caption = response.text.strip()
            logger.info(f"Gemini base caption generated: {caption[:100]}...")
            return caption

        except Exception as e:
            logger.error(f"Gemini File API caption failed: {e}")
            # Try frame-based fallback within Gemini
            return self._gemini_frame_caption(video_path, str(e))

    def _gemini_frame_caption(self, video_path: str, original_error: str) -> str:
        """Fallback: extract frames locally and send as images to Gemini."""
        try:
            import cv2
            from PIL import Image

            cap = cv2.VideoCapture(video_path)
            pil_frames = []

            if cap.isOpened():
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if frame_count > 0:
                    num_frames = min(10, frame_count)
                    indices = [int(i * frame_count / num_frames) for i in range(num_frames)]
                    for idx in indices:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                        ret, frame = cap.read()
                        if ret:
                            frame = cv2.resize(frame, (640, 360))
                            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            pil_frames.append(Image.fromarray(rgb))
            cap.release()

            if not pil_frames:
                raise Exception("Could not extract any frames from video.")

            prompt = """These are evenly-spaced frames from a video. Analyze them carefully.

Write a detailed, factual 3-4 sentence paragraph describing exactly what happens:
- Who/what is in the video
- What specific actions occur
- The setting and environment
- How things change across the frames

Be concrete and specific. Do NOT be generic. Output ONLY the description."""

            contents = pil_frames + [prompt]
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=600
                )
            )
            return response.text.strip()

        except Exception as e2:
            logger.error(f"Gemini frame caption also failed: {e2}")
            return self._fireworks_vision_caption(video_path)

    def _fireworks_vision_caption(self, video_path: str) -> str:
        """Last resort: extract frames and send to Fireworks Llama Vision."""
        try:
            import cv2
            import base64

            cap = cv2.VideoCapture(video_path)
            b64_frames = []

            if cap.isOpened():
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if frame_count > 0:
                    num_frames = min(8, frame_count)
                    indices = [int(i * frame_count / num_frames) for i in range(num_frames)]
                    for idx in indices:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                        ret, frame = cap.read()
                        if ret:
                            frame = cv2.resize(frame, (640, 360))
                            _, buffer = cv2.imencode('.jpg', frame)
                            b64_frames.append(base64.b64encode(buffer).decode('utf-8'))
            cap.release()

            if not b64_frames:
                return "A video was uploaded but could not be analyzed. Please check your API keys."

            prompt = """These are evenly-spaced frames from a video. Analyze them carefully.

Write a detailed, factual 3-4 sentence paragraph describing exactly what happens:
- Who/what is in the video  
- What specific actions occur
- The setting and environment

Be concrete and specific. Do NOT be generic. Output ONLY the description."""

            from .llm_service import LLMService
            llm = LLMService()
            return llm.generate_vision(prompt, b64_frames)

        except Exception as e:
            logger.error(f"Fireworks vision caption also failed: {e}")
            return "A video was submitted for analysis. Please ensure your GEMINI_API_KEY or FIREWORKS_API_KEY is set correctly in your environment."
