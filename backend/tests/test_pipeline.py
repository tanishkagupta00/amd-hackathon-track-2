import pytest
import os
from pipeline.video_preprocessor import VideoPreprocessor
from pipeline.frame_sampler import FrameSampler
from pipeline.scene_detector import SceneDetector
from pipeline.vision_engine import VisionEngine
from pipeline.temporal_reasoner import TemporalReasoner
from pipeline.caption_generator import CaptionGenerator
from pipeline.style_transformer import StyleTransformer
from pipeline.caption_critic import CaptionCritic

def test_video_preprocessor():
    preprocessor = VideoPreprocessor()
    # Test with a mock URL path
    metadata = preprocessor.validate_and_extract("https://example.com/test_developer.mp4")
    assert metadata["filename"] == "test_developer.mp4"
    assert metadata["duration"] == 15.0
    assert metadata["status"] == "validated_mocked"

def test_frame_sampler_and_scene_detector():
    sampler = FrameSampler(max_frames=3)
    keyframes = sampler.sample_keyframes("https://example.com/test_cat.mp4")
    assert len(keyframes) > 0
    assert keyframes[0]["is_mock"] is True

    detector = SceneDetector()
    scenes = detector.detect_scenes(keyframes)
    assert len(scenes) > 0
    assert scenes[0]["scene_id"] == 1

def test_vision_and_temporal_reasoning():
    detector = SceneDetector()
    sampler = FrameSampler(max_frames=3)
    keyframes = sampler.sample_keyframes("https://example.com/test_office.mp4")
    scenes = detector.detect_scenes(keyframes)

    engine = VisionEngine()
    analysis = engine.analyze_scene(scenes[0], "test_office.mp4")
    assert "developer" in analysis["objects"]
    assert "modern office desk" == analysis["location"]

    reasoner = TemporalReasoner()
    timeline = reasoner.build_timeline([analysis])
    assert len(timeline["timeline"]) == 1
    assert "developer" in timeline["entities"]

def test_generation_style_and_critic():
    reasoner = TemporalReasoner()
    engine = VisionEngine()
    analysis = engine.analyze_scene({"scene_id": 1, "start_time": 0.0, "end_time": 5.0}, "test_cat.mp4")
    timeline = reasoner.build_timeline([analysis])

    generator = CaptionGenerator()
    base_caption = generator.generate_base_caption(timeline)
    assert "cat" in base_caption

    transformer = StyleTransformer()
    sarcastic = transformer.transform(base_caption, "sarcastic", timeline["entities"])
    assert len(sarcastic) > 0

    critic = CaptionCritic()
    eval_res = critic.evaluate_caption(sarcastic, "sarcastic", timeline["entities"])
    assert eval_res["accuracy_score"] > 0.0
    assert eval_res["style_score"] > 0.0
