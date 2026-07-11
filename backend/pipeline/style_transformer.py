from .llm_service import LLMService

class StyleTransformer:
    def __init__(self):
        self.llm_service = LLMService()

    def transform(self, base_caption: str, style: str) -> str:
        """
        Transforms the baseline factual caption into the requested style via LLM rewrite.
        Uses Fireworks AI by default, falling back to Gemini if it fails.
        """
        system_content, user_content = self._build_prompts(base_caption, style)
        
        try:
            text = self.llm_service.generate_text(system_content, user_content)
            if text:
                return text
        except Exception as e:
            return f"[{style.upper()}] Error transforming style: {str(e)}"
            
        return base_caption

    def _build_prompts(self, base_caption: str, style: str) -> tuple[str, str]:
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
        
        user_content = (
            "Example translation:\n"
            f"Input Style: {style_prompt}\n"
            "Input Description: A cat sitting on a mat.\n"
            "Output: A feline creature resting upon a woven floor covering.\n\n"
            "Now translate the following:\n"
            f"Input Style: {style_prompt}\n"
            f"Input Description: {base_caption}\n"
            "Output:"
        )
        
        return system_content, user_content
