import cv2
import torch
import open_clip
from PIL import Image
import numpy as np

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Running on: {device}")

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)

model = model.to(device)
model.eval()
tokenizer = open_clip.get_tokenizer("ViT-B-32")

print("OpenCLIP loaded successfully!")

# Define a broad set of descriptive labels for zero-shot classification
CANDIDATE_LABELS = [
    "indoor setting", "outdoor setting", "person speaking to camera", 
    "people interacting", "computer programming or coding", "gaming", 
    "technology product", "nature or landscape", "animal", 
    "sports or physical activity", "cooking or food", "driving or vehicles",
    "presentation or lecture", "entertainment or music", "a cinematic scene"
]

def extract_visual_context(video_path: str) -> str:
    """
    Extracts representative frames from a video, runs them through OpenCLIP 
    zero-shot classification to detect scene context, and returns a summary.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return "Failed to open video for local processing."
            
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count <= 0:
            return "Video has no frames."
            
        # Sample up to 8 evenly spaced frames
        num_samples = min(8, frame_count)
        indices = np.linspace(0, frame_count - 1, num_samples, dtype=int)
        
        frames = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                # Convert BGR (OpenCV) to RGB (PIL)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)
                frames.append(preprocess(pil_img).unsqueeze(0))
                
        cap.release()
        
        if not frames:
            return "Failed to extract frames."
            
        # Stack frames into a batch
        image_input = torch.cat(frames).to(device)
        text_input = tokenizer(CANDIDATE_LABELS).to(device)
        
        with torch.no_grad():
            image_features = model.encode_image(image_input)
            text_features = model.encode_text(text_input)
            
            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            
            # Compute similarity: shape (num_frames, num_labels)
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            
            # Average predictions across all frames to get video-level context
            video_similarity = similarity.mean(dim=0)
            
        # Get top 3 predicted labels
        values, top_indices = video_similarity.topk(3)
        top_labels = [CANDIDATE_LABELS[idx.item()] for idx in top_indices]
        
        context = f"Detected visual themes: {', '.join(top_labels)}."
        return context
        
    except Exception as e:
        print(f"Error extracting visual context: {e}")
        return f"Local vision processing failed: {str(e)}"
