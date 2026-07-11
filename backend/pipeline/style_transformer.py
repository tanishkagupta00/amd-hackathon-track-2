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
            "You are a strict text restyler API. You MUST output ONLY the final translated text and NOTHING else. "
            "Do NOT include any reasoning, thoughts, analysis, numbered lists, or conversational filler."
        )
        
        user_content = (
            f"Input Style: {style_prompt}\n"
            f"Input Description: {base_caption}\n\n"
            "Output the final translated text directly. NO reasoning, NO analysis, NO introductory text. Just the 1-2 sentence translation."
        )
        
        return system_content, user_content
