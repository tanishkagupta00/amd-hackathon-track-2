# Backend Architecture

**Project:** CaptionForge AI  
**Document:** 15_Backend_Architecture.md  
**Version:** 1.0 (Iteration 1)

---

# 1. Executive Summary

This document defines the production-ready backend architecture for CaptionForge AI, including project structure, service layers, AI orchestration, configuration, logging, and deployment-ready patterns.

# 2. Architecture Goals

- Modular
- Scalable
- Testable
- Observable
- Docker-first
- API-first

# 3. Technology Stack

- Python 3.11
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- OpenCV
- FFmpeg
- PyTorch
- Transformers
- Uvicorn

# 4. Project Structure

```text
backend/
├── api/
├── core/
├── config/
├── services/
├── pipeline/
├── models/
├── schemas/
├── repositories/
├── workers/
├── utils/
├── tests/
└── main.py
```

# 5. Layered Architecture

Presentation Layer
- FastAPI Routes

Application Layer
- Services

Domain Layer
- AI Pipeline
- Business Logic

Persistence Layer
- Repositories
- Database

Infrastructure Layer
- Logging
- Storage
- Configuration

# 6. Core Services

- VideoService
- CaptionService
- EvaluationService
- ExportService
- HealthService
- ConfigService

# 7. AI Pipeline Modules

- VideoPreprocessor
- FrameSampler
- SceneDetector
- VisionEngine
- TemporalReasoner
- SemanticMemory
- CaptionPlanner
- CaptionGenerator
- StyleTransformer
- CaptionCritic
- RankingEngine

# 8. Dependency Injection

Shared services are injected into API endpoints to improve testability and loose coupling.

# 9. Configuration

Environment-driven configuration using .env files with separate profiles for development, testing, and production.

# 10. Logging

Structured JSON logging with request IDs, stage timings, and error traces.

# Iteration Status

Completed:
- Executive Summary
- Technology Stack
- Folder Structure
- Layered Architecture
- Core Services
- AI Modules
- Dependency Injection
- Configuration
- Logging

Next Iteration:
- Background jobs
- Exception handling
- Middleware
- Repository pattern
- Testing architecture
- Performance tuning
- Deployment integration
- Final sign-off
