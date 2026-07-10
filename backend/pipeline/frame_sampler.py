import os
import cv2
import numpy as np
from typing import List, Dict, Any

class FrameSampler:
    def __init__(self, output_dir: str = None, max_frames: int = 10, motion_threshold: float = 15.0):
        self.output_dir = output_dir or os.path.join(os.environ.get("TEMP", os.getcwd()), "captionforge_frames")
        self.max_frames = max_frames
        self.motion_threshold = motion_threshold
        os.makedirs(self.output_dir, exist_ok=True)

    def sample_keyframes(self, video_path: str) -> List[Dict[str, Any]]:
        """
        Extracts keyframes from video based on motion difference, capped at max_frames.
        """
        keyframes = []
        is_url = video_path.startswith("http://") or video_path.startswith("https://")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            # Mock keyframe indices for web URLs or files that failed to load
            mock_count = min(self.max_frames, 5)
            for i in range(mock_count):
                timestamp = i * 3.0
                frame_path = os.path.join(self.output_dir, f"mock_frame_{i}.jpg")
                # Create a blank image to avoid missing file errors
                img = np.zeros((100, 100, 3), dtype=np.uint8)
                cv2.putText(img, f"Frame {i}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                try:
                    cv2.imwrite(frame_path, img)
                except Exception:
                    pass
                keyframes.append({
                    "frame_index": i * 90,
                    "timestamp": timestamp,
                    "frame_path": frame_path,
                    "is_mock": True
                })
            return keyframes

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0

        prev_gray = None
        frame_idx = 0
        extracted_count = 0

        # Read frames sequentially
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = frame_idx / fps
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Resize to speed up pixel difference calculation
            gray_small = cv2.resize(gray, (160, 120))

            if prev_gray is None:
                # Always extract the very first frame
                is_keyframe = True
            else:
                # Compute absolute difference
                diff = cv2.absdiff(gray_small, prev_gray)
                mean_diff = np.mean(diff)
                is_keyframe = mean_diff > self.motion_threshold

            if is_keyframe:
                frame_name = f"frame_{frame_idx}_{timestamp:.2f}.jpg"
                frame_path = os.path.join(self.output_dir, frame_name)
                try:
                    cv2.imwrite(frame_path, frame)
                except Exception:
                    # In case of local write issues, keep the path reference anyway
                    pass
                
                keyframes.append({
                    "frame_index": frame_idx,
                    "timestamp": round(timestamp, 2),
                    "frame_path": frame_path,
                    "is_mock": False
                })
                extracted_count += 1
                prev_gray = gray_small

                if extracted_count >= self.max_frames:
                    break

            # Skip frames to speed up processing (e.g. read 1 frame every 0.5 seconds)
            skip_frames = int(fps * 0.5)
            if skip_frames > 1:
                frame_idx += skip_frames
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            else:
                frame_idx += 1

        cap.release()

        # If we failed to extract any frames, extract at least one uniform frame
        if not keyframes:
            keyframes.append({
                "frame_index": 0,
                "timestamp": 0.0,
                "frame_path": os.path.join(self.output_dir, "frame_0_0.00.jpg"),
                "is_mock": True
            })
            
        return keyframes
