import os
import logging
from typing import Dict, Any, List
from .caption_generator import CaptionGenerator
from .style_transformer import StyleTransformer
from .caption_critic import CaptionCritic

logger = logging.getLogger("captionforge.pipeline")

class CaptionForgePipeline:
    def __init__(self):
        self.caption_generator = CaptionGenerator()
        self.style_transformer = StyleTransformer()
        self.critic = CaptionCritic()

    def process_video(self, video_path: str, progress_callback = None) -> Dict[str, Any]:
        """
        Runs the full video captioning pipeline.
        """
        # Helper to send log updates to frontend long-polling/sockets if running
        def update_progress(stage: str, msg: str):
            logger.info(f"[{stage}] {msg}")
            if progress_callback:
                progress_callback(stage, msg)

        update_progress("uploading", "Uploading video to Gemini for multimodal analysis...")
        update_progress("analyzing", "Watching the entire video to extract subjects, actions, and audio...")
        
        base_caption = self.caption_generator.generate_base_caption(video_path)
        update_progress("analyzing", f"Base caption generated: '{base_caption}'")

        update_progress("generating", "Running parallel multi-head style transformer & critic feedback loop...")
        styles = ["formal", "sarcastic", "humorous-tech", "humorous-non-tech"]
        captions = {}
        evaluations = {}

        for style in styles:
            # Transform
            styled_text = self.style_transformer.transform(base_caption, style)
            # Critic
            eval_result = self.critic.evaluate_caption(styled_text, style, [])
            
            captions[style] = eval_result["caption"]
            evaluations[style] = {
                "accuracy_score": eval_result["accuracy_score"],
                "style_score": eval_result["style_score"],
                "hallucination_detected": eval_result["hallucination_detected"],
                "hallucinated_words": eval_result["hallucinated_words"],
                "style_reasons": eval_result["style_reasons"]
            }
            update_progress("generating", f"Compiled '{style}' style caption with accuracy: {eval_result['accuracy_score']}.")

        update_progress("completed", "Pipeline run finished successfully.")

        # Return a simplified dictionary, maintaining frontend compatibility
        return {
            "metadata": {"filename": os.path.basename(video_path)},
            "temporal_graph": {"entities": []},
            "base_caption": base_caption,
            "captions": captions,
            "evaluations": evaluations
        }

