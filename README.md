# 🎬 CaptionForge AI

**CaptionForge AI** is a robust, hardware-accelerated video captioning platform engineered exclusively for **Track 2 (Video Captioning Agent)** of the **AMD Developer Hackathon**. 

We tackle the challenge of intelligent video understanding by utilizing a highly modular **Extract-Reason-Style** pipeline. The system processes videos using AMD GPU-accelerated local visual encoding, reasons about the content, and dynamically restyles the output into four bespoke target styles:

- **Formal**: Objective, professional, third-person reports.
- **Sarcastic**: Dry, ironic, and mocking commentary.
- **Humorous-Tech**: Software engineering and hardware metaphors.
- **Humorous-Non-Tech**: Observational situational comedy.

---

## ✨ Key Features for Judges

* **AMD Hardware Acceleration**: Core visual context extraction and video frame sampling run entirely locally, fully utilizing AMD GPU architecture via PyTorch and OpenCLIP (`ViT-B-32`).
* **Resilient AI Fallback Architecture**: A custom `LLMService` handles styling and reasoning, automatically failing over across multiple Fireworks AI models (DeepSeek-V4-Pro → Kimi-K2 → GPT-OSS-120B) to ensure 100% uptime even if a primary model is rate-limited or unavailable.
* **Premium User Experience**: A breathtaking, responsive React frontend featuring GSAP-powered scroll animations, smooth morphing transitions, and an elegant Obsidian/AI-Gold dark theme.
* **Dual Execution Modes**: 
  - **Headless CLI Runner**: Automated, non-interactive execution reading from `tasks.json` to write compliance-checked outputs for batch judge evaluation.
  - **Interactive Dashboard**: Real-time visual pipeline monitoring and side-by-side comparative styled caption matrix.
* **Deployment Flexibility**: Designed to run seamlessly on AMD Cloud GPU Jupyter environments while remaining perfectly compatible with Vercel serverless deployments.

---

## 🛠️ Technology Stack

**Frontend**
* **Framework:** React 18, Vite, TypeScript
* **Styling & UI:** Tailwind CSS, Vanilla CSS, Lucide React (Icons)
* **Animation:** GSAP (ScrollTrigger, Custom Vanilla Text Splitters)

**Backend & Pipeline**
* **Framework:** FastAPI (Python 3.10+), SQLAlchemy (SQLite)
* **Vision Processing (AMD Local):** `torch`, `open_clip_torch`, `opencv-python`, `Pillow`
* **LLM Integration:** `openai` (Fireworks AI compatible)
* **Resilience:** Custom Exception Handling & Automated Fireworks Model Fallback Routing

---

## 🚀 Installation & Setup

### Prerequisite
Ensure Python 3.10+ and Node.js v18+ are installed.

### 1. Configure AMD GPU Backend
To leverage the AMD Hardware for local visual extraction:
```bash
# Install all required PyTorch, OpenCLIP, and FastAPI dependencies
pip install -r requirements.txt

# Start the server (Runs on port 8000)
python backend/main.py
```
*API documentation is automatically available at `http://localhost:8000/docs`.*

### 2. Configure React Frontend
```bash
cd frontend
npm install
npm run dev
```
*The web dashboard will instantly be available at `http://localhost:3000`.*

---

## 🤖 Running the Headless Evaluation CLI

CaptionForge AI provides a headless automated mode explicitly designed for batch evaluation.

Create a `tasks.json` in the project root:
```json
[
  {
    "task_id": "video_01",
    "video_path": "https://example.com/sample.mp4"
  }
]
```

**Execute the Runner:**
```bash
python backend/runner.py
```
This will parse the tasks, process the videos through the local AMD-accelerated pipeline, apply the fallback style generation, and output compliance-checked results to `results.json` conforming to the strict evaluation schema.
