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

            prompt = (
                "Watch this video clip carefully. Provide one detailed, factual scene description "
                "(a few sentences) capturing the actual content: the subject's actions, facial expressions, "
                "gestures, the setting, background details, the pacing, and explicitly transcribe or summarize "
                "any speech/audio content. Do not add any stylistic commentary or opinions."
            )
            
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
