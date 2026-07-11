from .llm_service import LLMService


class StyleTransformer:
    def __init__(self):
        self.llm_service = LLMService()

    def transform(self, base_caption: str, style: str) -> str:
        system_content, user_content = self._build_prompts(base_caption, style)
        try:
            text = self.llm_service.generate_text(system_content, user_content)
            if text:
                # Strip any reasoning leakage from models like DeepSeek/GLM
                # that sometimes prepend "I need to..." or "Let me think..."
                text = self._strip_reasoning(text.strip())
                return text
        except Exception as e:
            return f"[{style.upper()}] Style transformation failed: {str(e)}"
        return base_caption

    def _strip_reasoning(self, text: str) -> str:
        """
        Some models (DeepSeek, GLM) prepend chain-of-thought reasoning even when
        told not to. Strip any lines that look like internal monologue.
        """
        import re
        # Remove lines starting with reasoning patterns
        reasoning_patterns = [
            r"^(i need to|let me|i will|i should|the user wants|the task is|"
            r"analyze|here('s| is) (the|my)|okay,|alright,|sure,|certainly,|"
            r"of course,|first,|step \d)[,:\s].*",
        ]
        lines = text.split("\n")
        clean_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            is_reasoning = any(
                re.match(p, stripped, re.IGNORECASE)
                for p in reasoning_patterns
            )
            if not is_reasoning:
                clean_lines.append(line)

        result = "\n".join(clean_lines).strip()
        # If stripping removed everything, return original
        return result if result else text

    def _build_prompts(self, base_caption: str, style: str) -> tuple[str, str]:

        style_instructions = {
            "formal": (
                "Write in a formal, objective, third-person documentary register. "
                "Use precise academic or corporate language with passive-voice constructions. "
                "No humor, colloquialisms, slang, exclamation marks, or personal pronouns. "
                "Focus on observable actions, settings, and objects. "
                "Example: 'The subject proceeds to demonstrate the designated functionality, "
                "executing each operational step with systematic precision across the observed environment.'"
            ),
            "sarcastic": (
                "Write with biting, theatrical dry sarcasm. Treat every mundane action as if it is "
                "the most earth-shattering, unprecedented achievement in human history. "
                "Use dramatic overstatement, mock reverence, and ironic understatement. "
                "Be specific to the actual content — reference exactly what happens in the video. "
                "Use emphasis punctuation (dashes, ellipses) for comedic timing. "
                "Example: 'Behold — in a moment that will surely be studied by future generations, "
                "a human being has once again defied all expectations by... doing the exact thing "
                "anyone in that situation would obviously do. Truly, we are witnessing history.'"
            ),
            "humorous-tech": (
                "Write as a senior software engineer describing everyday life entirely through "
                "programming and DevOps metaphors. Every human action maps to a computing concept. "
                "Reference: stack traces, null pointers, merge conflicts, deployment failures, "
                "memory leaks, infinite loops, race conditions, legacy code, technical debt, "
                "garbage collection, API timeouts, segfaults, git blame, hotfixes, etc. "
                "Be specific to what actually happens in the video. "
                "Example: 'The user initiated a live production deploy of their morning routine, "
                "immediately triggering a NullPointerException when the coffee dependency "
                "returned undefined — classic. A hotfix was pushed, but the build pipeline "
                "has been flaky since Tuesday.'"
            ),
            "humorous-non-tech": (
                "Write warm, relatable, observational everyday comedy. "
                "Find the universal human truth in the mundane moment. "
                "Reference everyday struggles, relatable tropes, and slice-of-life irony "
                "that any general audience would immediately recognise. "
                "Absolutely NO tech or programming references. "
                "Be specific to the actual people and actions shown. "
                "Example: 'Ah yes, the timeless ritual — doing that one thing we all do, "
                "convincing ourselves it will only take five minutes, and then somehow "
                "it is forty-five minutes later and we have achieved both everything and nothing.'"
            ),
        }

        style_desc = style_instructions.get(style, "Rewrite in an engaging, creative style.")

        system_content = (
            "You are an expert caption writer. "
            "OUTPUT RULES — follow these exactly:\n"
            "1. Output ONLY the final caption text. Nothing else.\n"
            "2. No preamble, no reasoning, no explanation, no labels.\n"
            "3. Do not start with 'I', 'Let me', 'Here is', 'Sure', 'Certainly', or similar.\n"
            "4. Do not use bullet points, headers, or numbered lists.\n"
            "5. Write 3-4 sentences as a single flowing paragraph.\n"
            "6. Start directly with the caption content."
        )

        user_content = (
            f"STYLE: {style_desc}\n\n"
            f"SOURCE VIDEO DESCRIPTION:\n{base_caption}\n\n"
            "INSTRUCTION: Rewrite the source description in the style above. "
            "Stay specific to the actual events, people, and objects described. "
            "Do NOT be generic or vague. "
            "Write exactly 3-4 sentences as one paragraph.\n\n"
            "CAPTION:"
        )

        return system_content, user_content
