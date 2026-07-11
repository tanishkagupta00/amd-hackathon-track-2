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
        by genuinely watching and listening to the video via Gemini Multimodal.
        """
        if not self.client:
            return "No API key found. The subject is performing an action in a setting."
        
        try:
            # Upload video file to Gemini
            video_file = self.client.files.upload(file=video_path)
            
            # Wait for processing to complete
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = self.client.files.get(name=video_file.name)
            
            if video_file.state.name == "FAILED":
                return "Failed to process video via Gemini API."

            from .vision_encoder import extract_visual_context
            visual_context = extract_visual_context(video_path)

            prompt = f"""
Visual context extracted locally using AMD GPU:

{visual_context}

Now watch the ENTIRE video carefully.

Generate a factual description including:

- actions
- setting
- objects
- emotions
- speech
"""
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[video_file, prompt]
            )
            
            # Clean up the uploaded file to prevent quota issues
            try:
                self.client.files.delete(name=video_file.name)
            except:
                pass
                
            return response.text.strip()
        except Exception as e:
            return f"Error analyzing video: {str(e)}"
