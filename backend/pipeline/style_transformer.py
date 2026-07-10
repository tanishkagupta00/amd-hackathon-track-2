import os
from google import genai

class StyleTransformer:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def transform(self, base_caption: str, style: str) -> str:
        """
        Transforms the baseline factual caption into the requested style via LLM rewrite.
        """
        if not self.client:
            return f"[{style.upper()}] {base_caption}"
            
        prompt = self._get_prompt(base_caption, style)
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            text = response.text.strip()
            if text:
                return text
        except Exception as e:
            return f"[{style.upper()}] Error transforming style: {str(e)}"
            
        return base_caption

    def _get_prompt(self, base_caption: str, style: str) -> str:
        base_instruction = (
            f"Here is a factual scene description of a video:\n'{base_caption}'\n\n"
            "Your task is to completely rewrite this description from scratch into the requested style. "
            "Do NOT just prepend a fixed phrase to the original sentence. The output should differ entirely "
            "in wording, structure, and the specific details emphasized to fit the tone. "
            "Return ONLY the rewritten caption text, no markdown formatting or intro phrases."
        )
        
        if style == "formal":
            return f"{base_instruction}\nStyle: Highly objective, formal, third-person report. No conversational words or humor."
        elif style == "sarcastic":
            return f"{base_instruction}\nStyle: Dry, ironic, mocking, and sarcastic tone. Treat the mundane actions as if they are ridiculous or overly dramatic."
        elif style == "humorous-tech":
            return f"{base_instruction}\nStyle: Humorous paragraph heavily featuring software development, programming, or computer science jokes and metaphors (e.g., merge conflicts, legacy code, buffering)."
        elif style == "humorous-non-tech":
            return f"{base_instruction}\nStyle: Observational comedy with general, everyday relatable humor and tropes. Do NOT use any programming/tech jokes."
        return base_caption
