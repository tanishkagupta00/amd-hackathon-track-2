# Database Design


---

# 19. Complete SQL DDL Strategy

The production database targets PostgreSQL 16+.

## Core Tables
- videos
- scenes
- frames
- detected_objects
- actions
- semantic_memory
- captions
- evaluations
- exports

## Example DDL

```sql
CREATE TABLE videos (
    id UUID PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    duration DOUBLE PRECISION,
    fps DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

# 20. Redis Cache Strategy

Redis is optional for the hackathon but recommended for production.

Cached Items:
- Video metadata
- Scene summaries
- Prompt templates
- Model configuration

TTL:
- Metadata: 1 hour
- Prompt cache: 24 hours

---

# 21. Object Storage

Competition:
- Local filesystem

Production:
- Amazon S3 / MinIO

Directory Layout

```text
storage/
  videos/
  frames/
  outputs/
```

---

# 22. Analytics Schema

Metrics Collected

- Processing time
- Average caption score
- Hallucination rate
- Model latency
- Success rate

---

# 23. Backup & Recovery

- Daily PostgreSQL backup
- Weekly object storage snapshot
- Prompt version archive
- Automated restore validation

---

# 24. Final Recommendations

Competition Mode:
- Stateless processing
- JSON outputs
- Temporary storage only

Production Mode:
- PostgreSQL
- Redis
- Object Storage
- Alembic migrations
- SQLAlchemy ORM

---

# Final Sign-off

Status: APPROVED

This document defines the complete logical and physical data architecture for CaptionForge AI and serves as the implementation reference for persistence, schemas, caching, and future production deployment.
