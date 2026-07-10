import os
from openai import OpenAI

class StyleTransformer:
    def __init__(self):
        self.api_key = os.environ.get("FIREWORKS_API_KEY")
        if self.api_key:
            self.client = OpenAI(
                base_url="https://api.fireworks.ai/inference/v1",
                api_key=self.api_key
            )
        else:
            self.client = None

    def transform(self, base_caption: str, style: str) -> str:
        """
        Transforms the baseline factual caption into the requested style via LLM rewrite.
        """
        if not self.client:
            return f"[{style.upper()}] {base_caption}"
            
        messages = self._build_messages(base_caption, style)
        try:
            # Using glm-5p1 as specified in the hackathon integration guide
            response = self.client.chat.completions.create(
                model="accounts/fireworks/models/glm-5p1",
                messages=messages,
                max_tokens=600,
                temperature=0.7
            )
            text = response.choices[0].message.content.strip()
            if text:
                return text
        except Exception as e:
            return f"[{style.upper()}] Error transforming style: {str(e)}"
            
        return base_caption

    def _build_messages(self, base_caption: str, style: str) -> list[dict]:
        style_prompt = ""
        if style == "formal":
            style_prompt = "Highly objective, formal, third-person report. No conversational words or humor."
        elif style == "sarcastic":
            style_prompt = "Dry, ironic, mocking, and sarcastic tone. Treat the mundane actions as if they are ridiculous or overly dramatic."
        elif style == "humorous-tech":
            style_prompt = "Humorous paragraph heavily featuring software development, programming, or computer science jokes and metaphors (e.g., merge conflicts, legacy code, buffering)."
        elif style == "humorous-non-tech":
            style_prompt = "Observational comedy with general, everyday relatable humor and tropes. Do NOT use any programming/tech jokes."
            
        system_content = (
            "You are a direct translation API. You DO NOT think, you DO NOT analyze, and you DO NOT output numbered lists. "
            "You instantly output the final translated text and nothing else."
        )
        
        return [
            {"role": "system", "content": system_content},
            {
                "role": "user", 
                "content": f"Style: {style_prompt}\nDescription: A cat sitting on a mat."
            },
            {
                "role": "assistant",
                "content": "A feline creature resting upon a woven floor covering."
            },
            {
                "role": "user", 
                "content": f"Style: {style_prompt}\nDescription: {base_caption}"
            }
        ]
