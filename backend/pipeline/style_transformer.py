from .llm_service import LLMService


class StyleTransformer:
    def __init__(self):
        self.llm_service = LLMService()

    def transform(self, base_caption: str, style: str) -> str:
        """
        Transforms the baseline factual caption into the requested style via LLM rewrite.
        Uses Fireworks AI (Llama 3.1 70B) by default, falling back to Gemini if it fails.
        """
        system_content, user_content = self._build_prompts(base_caption, style)

        try:
            text = self.llm_service.generate_text(system_content, user_content)
            if text:
                return text.strip()
        except Exception as e:
            return f"[{style.upper()}] Style transformation failed: {str(e)}"

        return base_caption

    def _build_prompts(self, base_caption: str, style: str) -> tuple[str, str]:
        style_instructions = {
            "formal": (
                "Formal, objective, third-person documentary style. "
                "Use precise, passive-voice corporate language. "
                "No humor, slang, or emotional language. "
                "Example output: 'The subject demonstrates proficiency in the designated task, "
                "executing each action with measurable efficiency.'"
            ),
            "sarcastic": (
                "Biting, dry sarcasm and irony. Treat every mundane action as if it is "
                "the most absurd, dramatic, groundbreaking thing ever witnessed. "
                "Mock the subject lovingly. Be theatrical. "
                "Example output: 'Absolutely riveting. In a stunning display of human achievement, "
                "someone has once again defied all expectations by doing exactly what anyone would do.'"
            ),
            "humorous-tech": (
                "Hilarious tech/developer humor. Describe the video using software engineering, "
                "coding, DevOps, and computer science metaphors. "
                "Reference things like merge conflicts, legacy code, runtime errors, "
                "buffer overflows, infinite loops, deployment failures, stack traces, etc. "
                "Example output: 'The user attempted a live refactor of their physical workflow, "
                "only to encounter an unexpected NullPointerException when the coffee variable returned undefined.'"
            ),
            "humorous-non-tech": (
                "Warm, relatable, everyday observational comedy. "
                "Find the funny in the mundane. Reference universal human experiences, "
                "everyday struggles, common tropes, and slice-of-life humor. NO tech jokes. "
                "Example output: 'Ah yes, the classic story of a person doing that thing everyone does "
                "but nobody talks about — and somehow making it look both heroic and completely unnecessary.'"
            ),
        }

        style_desc = style_instructions.get(style, "Rewrite in an engaging, interesting style.")

        system_content = (
            "You are an expert creative writer and caption specialist. "
            "Your ONLY job is to output the final rewritten caption. "
            "Do NOT include any preamble, explanation, reasoning, or formatting. "
            "Just output the caption text directly."
        )

        user_content = (
            f"STYLE INSTRUCTIONS: {style_desc}\n\n"
            f"ORIGINAL VIDEO DESCRIPTION:\n{base_caption}\n\n"
            "TASK: Rewrite the original video description in the style above. "
            "The rewrite MUST be specific to the actual events described — do NOT be vague or generic. "
            "Write a punchy, engaging 3-4 sentence paragraph that captures the exact content of the video "
            "but reframed through the target style lens.\n\n"
            "OUTPUT (only the final caption, nothing else):"
        )

        return system_content, user_content
