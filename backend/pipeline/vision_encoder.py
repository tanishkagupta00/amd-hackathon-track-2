import torch
import open_clip

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Running on: {device}")

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)

model = model.to(device)
model.eval()

print("OpenCLIP loaded successfully!")
