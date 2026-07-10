# CaptionForge AI

CaptionForge AI is an AI-powered video captioning platform built for Track 2 (Video Captioning Agent) of the AMD Developer Hackathon. It uses a modular **Extract-Reason-Style** multi-stage AI pipeline to analyze videos and generate captions in four distinct styles:
- **Formal**: Objective, professional, third-person reports.
- **Sarcastic**: Dry, ironic, and mocking commentary.
- **Humorous-Tech**: Software engineering and hardware metaphors.
- **Humorous-Non-Tech**: Observational situational comedy.

---

## Features

- **Decoupled AI Pipeline**: Video preprocessing, motion-aware keyframe sampling, scene detection, visual analysis, temporal reasoning, styled generation, and quality feedback loops.
- **Headless Runner CLI**: Non-interactive execution reading tasks from `/input/tasks.json` and writing results to `/output/results.json`.
- **FastAPI Backend REST Server**: High-performance HTTP server with endpoints for video ingestion, real-time log tracking, generation, and quality evaluation.
- **React Frontend Dashboard**: Premium, modern dashboard with drag-and-drop video upload, real-time visual pipeline monitor, and side-by-side comparative styled caption matrix.
- **Local Dev Resilience**: Automatically routes uploads, database, and keyframes to the system `TEMP` directory on Windows to bypass OneDrive path lock policies.

---

## Project Structure

```text
├── backend/
│   ├── api/            # API Router endpoints
│   ├── core/           # Configuration settings
│   ├── pipeline/       # Multi-stage Extract-Reason-Style pipeline
│   ├── schemas/        # Request/Response schemas (Pydantic validation)
│   ├── database.py     # SQLite history persistence (SQLAlchemy)
│   ├── main.py         # FastAPI App Entrypoint
│   └── runner.py       # Headless CLI Runner
├── frontend/           # React + Vite + Tailwind CSS dashboard
├── Dockerfile          # Multi-stage container compilation
├── entrypoint.sh       # Container entrypoint script
├── requirements.txt    # Python dependencies
└── README.md           # Setup manual
```

---

## Installation & Setup

### Prerequisite
Ensure Python 3.10+ and Node.js v18+ are installed.

### 1. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Backend Server
```bash
python backend/main.py
```
The server will start at `http://localhost:8000`. You can access API documentation at `http://localhost:8000/docs`.

### 3. Install & Start Frontend (Development)
```bash
cd frontend
npm install
npm run dev
```
The web dashboard will start at `http://localhost:3000`.

### 4. Build Frontend (Production)
```bash
cd frontend
npm run build
```
FastAPI will automatically serve the compiled frontend assets directly from `http://localhost:8000/`.

---

## Running the Headless CLI Runner

For evaluation, CaptionForge AI can run in a headless automated mode. Create a `tasks.json` in the root (or map it in Docker to `/input/tasks.json`):

```json
[
  {
    "task_id": "video_01",
    "video_path": "https://example.com/sample.mp4"
  }
]
```

Run the runner:
```bash
python backend/runner.py
```
This will output compliance-checked results to `results.json` (or `/output/results.json` in Docker) conforming to the evaluation schema.

---

## Running Unit Tests

Run the test suite using pytest:
```bash
pytest backend/tests/
```
