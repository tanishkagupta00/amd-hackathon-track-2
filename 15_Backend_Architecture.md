
# Backend Architecture

**Project:** CaptionForge AI  
**Document:** 15_Backend_Architecture.md  
**Version:** 2.0 (Implementation Aligned)

---

# 1. Executive Summary

This document defines the production-ready backend architecture for CaptionForge AI. The backend is built with FastAPI, uses SQLAlchemy for persistence, and integrates with Fireworks AI for GPU-accelerated inference.

**Current Implementation:**
- FastAPI application with CORS middleware
- SQLAlchemy ORM with SQLite database
- Modular pipeline architecture
- Fireworks AI integration for vision and language models
- Serverless-compatible design (Vercel deployment)

---

# 2. Architecture Goals

- ✅ Modular - Each service has one responsibility
- ✅ Scalable - Serverless-ready architecture
- ✅ Testable - Dependency injection and clean separation
- ✅ Observable - Structured logging throughout
- ✅ Docker-first - Containerized execution
- ✅ API-first - RESTful endpoints with OpenAPI docs

---

# 3. Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Framework | FastAPI | 0.110.0+ |
| Language | Python | 3.11+ |
| ORM | SQLAlchemy | 2.0+ |
| Validation | Pydantic | 2.6+ |
| Server | Uvicorn | 0.28.0+ |
| Video Processing | imageio, imageio-ffmpeg | 2.30.0+, 0.4.9+ |
| Image Processing | Pillow | 10.0.0+ |
| HTTP Client | requests, httpx | Latest |
| AI Integration | OpenAI SDK (Fireworks) | 1.12.0+ |

---

# 4. Project Structure

```
backend/
├── main.py                    # FastAPI app initialization
├── database.py                # SQLAlchemy models and session
├── runner.py                  # Headless CLI runner for Docker
├── __init__.py
│
├── core/
│   ├── config.py              # Settings (Pydantic BaseSettings)
│   └── __init__.py
│
├── api_v1/
│   ├── routes.py              # All API endpoints
│   └── __init__.py
│
├── pipeline/
│   ├── __init__.py
│   ├── pipeline.py            # Main orchestration
│   ├── caption_generator.py   # Vision + transcription
│   ├── style_transformer.py   # Multi-style generation
│   ├── caption_critic.py      # Quality evaluation
│   ├── llm_service.py         # LLM API client
│   └── vision_encoder.py      # (Not used in current impl)
│
├── schemas/
│   ├── models.py              # Pydantic request/response models
│   └── __init__.py
│
├── templates/
│   └── index.html             # Fallback landing page
│
└── tests/
    ├── test_api.py
    ├── test_pipeline.py
    ├── test_runner.py
    └── __init__.py
```

---

# 5. Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  FastAPI Routes (api_v1/routes.py)                          │
│  - Request validation                                        │
│  - Response serialization                                    │
│  - Error handling                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  Services & Orchestration                                    │
│  - CaptionForgePipeline                                      │
│  - Background task management                                │
│  - Progress callbacks                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        AI LAYER                              │
│  Pipeline Modules                                            │
│  - CaptionGenerator (vision + transcription)                │
│  - StyleTransformer (multi-style generation)                │
│  - CaptionCritic (evaluation)                               │
│  - LLMService (API abstraction)                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   PERSISTENCE LAYER                          │
│  Database (database.py)                                      │
│  - SQLAlchemy ORM                                            │
│  - VideoRecord model                                         │
│  - Session management                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                       │
│  - Configuration (core/config.py)                           │
│  - Logging (Python logging)                                 │
│  - File storage (local/tmpfiles.org)                        │
│  - Environment variables                                    │
└─────────────────────────────────────────────────────────────┘
```

---

# 6. Core Components

## 6.1 FastAPI Application (`main.py`)

```python
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)
```

## 6.2 API Routes (`api_v1/routes.py`)

| Endpoint | Method | Handler |
|----------|--------|---------|
| `/videos` | POST | `upload_video()` |
| `/videos/url` | POST | `upload_video_from_url()` |
| `/videos/{id}` | GET | `get_video_status()` |
| `/captions/generate` | POST | `generate_captions()` |
| `/captions/{id}` | GET | `get_captions()` |
| `/evaluations` | POST | `evaluate_caption()` |
| `/health` | GET | `health_check()` |
| `/config` | GET | `get_config()` |

## 6.3 Pipeline Orchestrator (`pipeline/pipeline.py`)

```python
class CaptionForgePipeline:
    def __init__(self):
        self.caption_generator = CaptionGenerator()
        self.style_transformer = StyleTransformer()
        self.critic = CaptionCritic()

    def process_video(self, video_path: str, progress_callback=None) -> Dict:
        # 1. Generate base caption
        base_caption = self.caption_generator.generate_base_caption(video_path)
        
        # 2. Transform into styles
        captions = {}
        for style in ["formal", "sarcastic", "humorous-tech", "humorous-non-tech"]:
            styled_text = self.style_transformer.transform(base_caption, style)
            
            # 3. Evaluate
            eval_result = self.critic.evaluate_caption(styled_text, style, [])
            captions[style] = eval_result["caption"]
        
        return {"captions": captions, "evaluations": evaluations}
```

---

# 7. Dependency Injection

```python
# Database session injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in endpoints
@router.post("/videos")
def upload_video(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    record = VideoRecord(id=video_id, filename=file.filename)
    db.add(record)
    db.commit()
    return VideoUploadResponse(video_id=video_id, status="uploaded")
```

---

# 8. Configuration Management

## 8.1 Settings (`core/config.py`)

```python
class Settings(BaseSettings):
    PROJECT_NAME: str = "CaptionForge AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    IS_WINDOWS: bool = os.name == 'nt'
    TEMP_DIR: str = os.environ.get("TEMP", "/tmp")
    
    @property
    def STORAGE_DIR(self) -> str:
        if self.IS_WINDOWS:
            d = os.path.join(self.TEMP_DIR, "captionforge_storage")
        else:
            d = "/tmp/captionforge_storage"
        os.makedirs(d, exist_ok=True)
        return d
    
    @property
    def DATABASE_URL(self) -> str:
        db_path = os.path.join(self.STORAGE_DIR, "captionforge.db")
        return f"sqlite:///{db_path}"
    
    class Config:
        case_sensitive = True

settings = Settings()
```

## 8.2 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FIREWORKS_API_KEY` | ✅ Yes | API key for Fireworks AI |
| `TEMP` | No | Temp directory (Windows) |

---

# 9. Logging

## 9.1 Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("captionforge.pipeline")
```

## 9.2 Log Points

| Component | Log Events |
|-----------|-----------|
| `routes.py` | Request received, response sent, errors |
| `pipeline.py` | Stage transitions, completion |
| `caption_generator.py` | Audio extraction, frame extraction, API calls |
| `llm_service.py` | Model selection, API errors, fallbacks |

---

# 10. Error Handling

## 10.1 HTTP Exceptions

```python
from fastapi import HTTPException

# Not found
raise HTTPException(status_code=404, detail="Video record not found")

# Validation error
raise HTTPException(status_code=400, detail="Invalid video format")

# Processing error
raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")
```

## 10.2 Graceful Degradation

- **No audio:** Skip transcription, continue with vision
- **Model rate limit:** Fall back to next model
- **Frame extraction failure:** Return clear error message

---

# 11. Background Jobs

## 11.1 Background Task Execution

```python
@router.post("/captions/generate")
def generate_captions(
    req: CaptionGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # For legacy mode, run in background
    background_tasks.add_task(
        run_pipeline_job, 
        req.video_id, 
        video_path, 
        SessionLocal
    )
```

## 11.2 Progress Callbacks

```python
def run_pipeline_job(video_id: str, video_path: str, db_session_factory):
    db = db_session_factory()
    try:
        record = db.query(VideoRecord).filter(VideoRecord.id == video_id).first()
        
        def on_progress(stage: str, msg: str):
            record.status = stage
            record.append_log(msg)
            db.commit()
        
        res = pipeline.process_video(video_path, progress_callback=on_progress)
        record.set_captions(res["captions"])
        db.commit()
    finally:
        db.close()
```

---

# 12. Serverless Compatibility

## 12.1 Vercel Deployment

The backend is designed for Vercel serverless functions:

```python
# api/index.py (Vercel entry point)
from main import app  # Import FastAPI app from backend/
```

**Key Considerations:**
- No persistent state between requests
- Database stored in temp directory (ephemeral)
- Videos uploaded to tmpfiles.org for persistence
- API calls to Fireworks AI for GPU compute

## 12.2 File Handling

```python
# Use temp directories
with tempfile.TemporaryDirectory() as tmpdir:
    video_path = os.path.join(tmpdir, "video.mp4")
    # Process video
    # Temp directory auto-cleaned
```

---

# 13. Headless Runner (`runner.py`)

For Docker-based evaluation:

```python
def main():
    input_file, output_file = get_io_paths()
    
    with open(input_file, "r") as f:
        tasks = json.load(f)
    
    pipeline = CaptionForgePipeline()
    results = []
    
    for task in tasks:
        res = pipeline.process_video(task["video_path"])
        results.append(TaskCaptionResult(
            task_id=task["task_id"],
            captions=res["captions"]
        ))
    
    with open(output_file, "w") as f:
        json.dump(submission.model_dump(by_alias=True), f, indent=2)
```

---

# 14. AMD Worker Service (`amd_worker/`)

Optional dedicated service for AMD MI300X GPUs:

```
amd_worker/
├── main.py            # FastAPI service for caption generation
├── requirements.txt   # Dependencies
└── README.md          # Documentation
```

**Purpose:** Process videos on dedicated AMD GPU hardware

**Endpoint:** `POST /generate_base_caption`

---

# 15. Final Sign-off

**Status:** ✅ IMPLEMENTATION ALIGNED

This document accurately reflects the current FastAPI backend architecture.

---

## Next Iteration (Production)

- Add request rate limiting
- Implement JWT authentication
- Add request/response logging middleware
- Set up Alembic migrations
- Add health check for Fireworks AI connectivity
- Implement caching for repeated requests

