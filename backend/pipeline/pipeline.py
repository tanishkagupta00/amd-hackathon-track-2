import os
import logging
from typing import Dict, Any, List
from .video_preprocessor import VideoPreprocessor
from .frame_sampler import FrameSampler
from .scene_detector import SceneDetector
from .vision_engine import VisionEngine
from .temporal_reasoner import TemporalReasoner
from .caption_generator import CaptionGenerator
from .style_transformer import StyleTransformer
from .caption_critic import CaptionCritic

logger = logging.getLogger("captionforge.pipeline")

class CaptionForgePipeline:
    def __init__(self):
        self.preprocessor = VideoPreprocessor()
        self.sampler = FrameSampler()
        self.scene_detector = SceneDetector()
        self.vision_engine = VisionEngine()
        self.temporal_reasoner = TemporalReasoner()
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

        update_progress("preprocessor", "Validating video file and extracting metadata...")
        metadata = self.preprocessor.validate_and_extract(video_path)
        
        update_progress("sampling", f"Decoding video and running motion-aware keyframe extraction...")
        keyframes = self.sampler.sample_keyframes(video_path)
        update_progress("sampling", f"Extracted {len(keyframes)} informative keyframes.")

        update_progress("sampling", "Running scene segmentation...")
        scenes = self.scene_detector.detect_scenes(keyframes)
        update_progress("sampling", f"Grouped keyframes into {len(scenes)} scenes.")

        update_progress("reasoning", "Performing spatial object & action tagging per scene...")
        scene_analyses = []
        for scene in scenes:
            analysis = self.vision_engine.analyze_scene(scene, metadata["filename"])
            scene_analyses.append(analysis)
            update_progress("reasoning", f"Analyzed Scene {scene['scene_id']}: detected {len(analysis['objects'])} entities.")

        update_progress("reasoning", "Synthesizing temporal timeline & action graph...")
        temporal_graph = self.temporal_reasoner.build_timeline(scene_analyses)

        update_progress("generating", "Generating factual base caption summary...")
        base_caption = self.caption_generator.generate_base_caption(temporal_graph)
        update_progress("generating", f"Base caption generated: '{base_caption}'")

        update_progress("generating", "Running parallel multi-head style transformer & critic feedback loop...")
        styles = ["formal", "sarcastic", "humorous-tech", "humorous-non-tech"]
        captions = {}
        evaluations = {}

        for style in styles:
            # Transform
            styled_text = self.style_transformer.transform(base_caption, style, temporal_graph["entities"])
            # Critic
            eval_result = self.critic.evaluate_caption(styled_text, style, temporal_graph["entities"])
            
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

        return {
            "metadata": metadata,
            "temporal_graph": temporal_graph,
            "base_caption": base_caption,
            "captions": captions,
            "evaluations": evaluations
        }
