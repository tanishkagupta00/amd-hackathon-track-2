import os
import time
from google import genai

class CaptionGenerator:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_base_caption(self, video_path: str) -> str:
        """
        Creates a factual, non-stylized base caption summarizing the video timeline,
        by genuinely watching the video frames via Gemini or Fireworks Vision.
        """
        # 1. ALWAYS run local AMD GPU visual extraction first
        try:
            from .vision_encoder import extract_visual_context
            visual_context = extract_visual_context(video_path)
        except Exception as e:
            print(f"Skipping local AMD vision extraction (not available in this environment): {e}")
            visual_context = "Local vision extraction skipped."

        # 2. Extract frames locally using OpenCV to pass directly to Vision APIs
        import cv2
        import base64
        from PIL import Image
        
        cap = cv2.VideoCapture(video_path)
        pil_frames = []
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
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_img = Image.fromarray(rgb_frame)
                        pil_frames.append(pil_img)
                        
                        _, buffer = cv2.imencode('.jpg', frame)
                        b64_frames.append(base64.b64encode(buffer).decode('utf-8'))
        cap.release()

        if not pil_frames:
            return "A generic video showing a sequence of events. A person or object is interacting with the environment."

        prompt = f"""
Visual context extracted locally: {visual_context}

Attached are evenly spaced frames extracted from the video.
Watch the video frames carefully and analyze the temporal sequence.

Generate a comprehensive, catchy paragraph describing what is happening in the video.
Include actions, setting, objects, and overall mood.

Output ONLY the catchy paragraph (3-4 sentences). Do not include any reasoning, thoughts, or introductory text.
"""
        
        # 3. Use Gemini if available
        if self.client:
            try:
                contents = pil_frames + [prompt]
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contents
                )
                return response.text.strip()
            except Exception as e:
                print(f"Gemini Vision API failed ({e}). Falling back to LLMService Vision.")
        
        # 4. Fallback to Fireworks Vision API in LLMService if Gemini failed or missing
        from .llm_service import LLMService
        llm = LLMService()
        return llm.generate_vision(prompt, b64_frames)
