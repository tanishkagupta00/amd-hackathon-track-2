
# System Architecture Document (SAD)

**Project:** CaptionForge AI  
**Document:** 10_System_Architecture.md  
**Version:** 2.0 (Implementation Aligned)

---

# Table of Contents

1. Executive Summary
2. Architectural Goals
3. Architecture Principles
4. Quality Attributes
5. System Context
6. High-Level Architecture
7. Actual Implementation Stack
8. Component Architecture

---

# 1. Executive Summary

CaptionForge AI is a production-grade multimodal video captioning platform designed for the AMD Developer Hackathon Track 2. The system processes videos through a multi-stage AI pipeline and generates captions in four required styles: **Formal, Sarcastic, Humorous-Tech, and Humorous-Non-Tech**.

**Current Implementation Status:** ✅ Fully Implemented

The architecture uses a decoupled **Extract-Reason-Style** multi-model approach, utilizing:
- **Fireworks AI** for vision and language models (running on AMD MI300X cloud GPUs)
- **FastAPI** backend with SQLite persistence
- **React + TypeScript** frontend with Vite build system
- **Serverless-first** design (Vercel-compatible)

---

# 2. Architectural Goals

## Primary Goals

- ✅ Produce accurate, style-aware captions
- ✅ Support four required caption styles
- ✅ Minimize hallucinations via structured extraction
- ✅ Work on unseen benchmark videos
- ✅ Execute reliably in Docker containers
- ✅ Serverless-compatible (Vercel deployment)

## Engineering Goals

- ✅ Modular AI pipeline services
- ✅ Loose coupling between components
- ✅ High cohesion within modules
- ✅ Testable architecture
- ✅ Configuration-driven behavior
- ✅ Production-ready error handling

---

# 3. Architecture Principles

## AI First

Business logic is centered around the multi-stage AI pipeline:
1. **Extract** → Video frames + audio
2. **Transcribe** → Speech to text via Whisper-v3
3. **Analyze** → Vision understanding via Kimi-k2p6
4. **Style** → Multi-head style transformation via DeepSeek-v4-pro
5. **Evaluate** → Quality scoring and hallucination detection

## Modular Components

Each module has one responsibility:
- `caption_generator.py` - Base caption synthesis
- `style_transformer.py` - Style-specific rewriting
- `caption_critic.py` - Quality evaluation
- `llm_service.py` - LLM API abstraction

## Stateless Processing

Pipeline stages avoid shared mutable state. All context flows through structured data objects passed between functions.

## API First

Every capability is exposed through RESTful FastAPI endpoints at `/api/v1/`.

## Cloud GPU Acceleration

Heavy compute (vision + LLM) runs on **AMD MI300X GPUs** via Fireworks AI, allowing serverless deployment on Vercel without local GPU requirements.

---

# 4. Quality Attributes

| Attribute | Target | Current Status |
|-----------|--------|----------------|
| Accuracy | Very High | ✅ Implemented |
| Reliability | High | ✅ Implemented |
| Maintainability | High | ✅ Implemented |
| Scalability | Medium | ✅ Serverless-ready |
| Observability | High | ✅ Logging enabled |
| Security | High | ✅ API key auth |
| Extensibility | High | ✅ Modular design |

---

# 5. System Context

## Actors

- **AMD Evaluation Platform** - Automated test harness
- **End Users** - Upload videos via web interface
- **AI Models** - Fireworks AI (Whisper, Kimi, DeepSeek)
- **Docker Runtime** - Containerized execution
- **Vercel Runtime** - Serverless deployment

## External Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| Fireworks AI API | Vision + LLM inference | ✅ Active |
| FFmpeg / imageio-ffmpeg | Audio/video processing | ✅ Bundled |
| Python 3.11+ | Runtime environment | ✅ Required |
| SQLite | Persistence layer | ✅ Embedded |

## System Boundary

The system receives video input (file upload or URL), performs AI processing, and returns benchmark-compliant JSON with four styled captions per video.

---

# 6. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  React + TypeScript Frontend (Vite build)                       │
│  - Drag & Drop Upload                                            │
│  - Progress Tracking                                             │
│  - Caption Display Cards                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                                │
│  FastAPI Gateway (api/index.py → backend/main.py)               │
│  - POST /videos, /videos/url                                     │
│  - POST /captions/generate                                       │
│  - GET /captions/{id}, /videos/{id}                             │
│  - POST /evaluations                                             │
│  - GET /health, /config                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      PIPELINE LAYER                              │
│  CaptionForgePipeline (backend/pipeline/pipeline.py)            │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐     │
│  │ Caption     │  │ Style        │  │ Caption           │     │
│  │ Generator   │→ │ Transformer  │→ │ Critic            │     │
│  └─────────────┘  └──────────────┘  └───────────────────┘     │
│         ↓                  ↓                    ↓               │
│  Fireworks AI:        Fireworks AI:       Local Rules:         │
│  - Whisper-v3         - DeepSeek-v4-pro   - Hallucination det  │
│  - Kimi-k2p6          - Fallback models   - Style scoring      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     PERSISTENCE LAYER                            │
│  SQLite (SQLAlchemy ORM)                                        │
│  - VideoRecord (id, filename, status, captions, evaluations)   │
│  - Stored in /tmp/captionforge_storage/                         │
└─────────────────────────────────────────────────────────────────┘
```

## Layered View

### Presentation Layer
- React frontend with TypeScript
- Drag-drop upload components
- Real-time progress tracking
- Four-card caption comparison view

### Application Layer
- FastAPI route handlers
- Request validation (Pydantic schemas)
- Background task orchestration
- Configuration management

### AI Layer
- CaptionGenerator - Base caption synthesis
- StyleTransformer - Multi-style rewriting
- CaptionCritic - Quality evaluation
- LLMService - Fireworks AI integration

### Infrastructure Layer
- SQLite database
- File storage (local/tmpfiles.org)
- Logging (Python logging)
- Environment configuration

---

# 7. Actual Implementation Stack

## Backend Stack
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | 0.110.0+ |
| ORM | SQLAlchemy | 2.0+ |
| Validation | Pydantic | 2.6+ |
| Server | Uvicorn | 0.28.0+ |
| Video Processing | imageio + imageio-ffmpeg | 2.30.0+ |
| Image Processing | Pillow | 10.0.0+ |
| HTTP Client | requests, httpx | Latest |

## Frontend Stack
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 18.3+ |
| Language | TypeScript | Strict mode |
| Build Tool | Vite | 5.x |
| Styling | Tailwind CSS | 3.4+ |
| State | Zustand | 4.5+ |
| HTTP Client | Axios | 1.6+ |

## AI/ML Stack
| Component | Model | Provider |
|-----------|-------|----------|
| Speech-to-Text | Whisper-v3 | Fireworks AI |
| Vision-Language | Kimi-k2p6 | Fireworks AI |
| Style Generation | DeepSeek-v4-pro | Fireworks AI |
| Fallback Models | Kimi-k2p6, GPT-OSS-120B | Fireworks AI |

---

# 8. Component Architecture

## Backend Components

```
backend/
├── main.py                    # FastAPI app initialization
├── database.py                # SQLAlchemy models
├── runner.py                  # Headless CLI runner
├── core/
│   └── config.py              # Settings (Pydantic)
├── api_v1/
│   └── routes.py              # All API endpoints
├── pipeline/
│   ├── pipeline.py            # Main orchestration
│   ├── caption_generator.py   # Vision + transcription
│   ├── style_transformer.py   # Multi-style generation
│   ├── caption_critic.py      # Quality evaluation
│   └── llm_service.py         # LLM API client
├── schemas/
│   └── models.py              # Pydantic request/response
└── templates/
    └── index.html             # Fallback UI
```

## Frontend Components

```
frontend/
├── src/
│   ├── App.tsx                # Route definitions
│   ├── pages/
│   │   ├── Home.tsx           # Landing page
│   │   └── Workspace.tsx      # Main workspace
│   ├── components/
│   │   ├── DragDrop.tsx       # Upload zone
│   │   └── CaptionOrbDemo.jsx # Demo component
│   └── apiConfig.ts           # API base URL
├── package.json
└── vite.config.ts
```

---

## Iteration Status

✅ Executive Summary - Updated to implementation  
✅ Architectural Goals - Verified against code  
✅ Architecture Principles - Aligned with Extract-Reason-Style  
✅ Quality Attributes - Confirmed  
✅ System Context - Updated with actual dependencies  
✅ High-Level Architecture - Reflects actual stack  
✅ Component Architecture - Matches actual code structure  

**Status:** ✅ IMPLEMENTATION ALIGNED

