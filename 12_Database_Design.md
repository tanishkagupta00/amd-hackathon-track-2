
# Database Design

**Project:** CaptionForge AI  
**Document:** 12_Database_Design.md  
**Version:** 2.0 (Implementation Aligned)

---

# 1. Executive Summary

CaptionForge AI uses a lightweight SQLite database for local development and hackathon execution. The database is managed through SQLAlchemy ORM and stores video processing metadata, captions, and evaluation results.

**Current Implementation:**
- **Database:** SQLite (embedded)
- **ORM:** SQLAlchemy 2.0+
- **Location:** `/tmp/captionforge_storage/captionforge.db` (Linux/Mac) or `%TEMP%\captionforge_storage\captionforge.db` (Windows)
- **Schema:** Single `videos` table with JSON columns

---

# 2. Database Architecture

## 2.1 Design Philosophy

- **Serverless-ready:** SQLite requires no external server
- **JSON flexibility:** Captions and evaluations stored as JSON strings
- **Single table design:** Simplified for hackathon scope
- **Ephemeral storage:** Database stored in temp directory

## 2.2 Connection Management

```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Required for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

---

# 3. Schema Definition

## 3.1 Videos Table

```python
# backend/database.py
class VideoRecord(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, index=True)           # UUID
    filename = Column(String, nullable=False)                    # Original filename
    status = Column(String, default="idle")                      # Processing status
    logs = Column(Text, default="")                               # Processing logs
    captions = Column(Text, default="{}")                         # JSON string
    evaluations = Column(Text, default="{}")                     # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
```

## 3.2 DDL (Data Definition Language)

```sql
CREATE TABLE videos (
    id VARCHAR(36) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'idle',
    logs TEXT DEFAULT '',
    captions TEXT DEFAULT '{}',
    evaluations TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_videos_id ON videos(id);
```

---

# 4. Status Values

| Status | Description |
|--------|-------------|
| `idle` | Initial state (rarely used) |
| `uploaded` | Video successfully uploaded |
| `queued` | Processing queued |
| `preprocessor` | Extracting frames/audio |
| `analyzing` | Running vision model |
| `generating` | Generating styled captions |
| `completed` | All processing finished |
| `failed` | Processing error occurred |

---

# 5. JSON Data Structures

## 5.1 Captions Column

```json
{
  "formal": "The subject demonstrates the functionality...",
  "sarcastic": "Behold, in a moment that will surely be studied...",
  "humorous-tech": "The user initiated a production deploy...",
  "humorous-non-tech": "Ah yes, the timeless ritual..."
}
```

## 5.2 Evaluations Column

```json
{
  "formal": {
    "accuracy_score": 0.95,
    "style_score": 0.90,
    "hallucination_detected": false,
    "hallucinated_words": [],
    "style_reasons": []
  },
  "sarcastic": {
    "accuracy_score": 0.95,
    "style_score": 0.85,
    "hallucination_detected": false,
    "hallucinated_words": [],
    "style_reasons": ["Sarcasm reads flat without emphasis punctuation"]
  }
}
```

---

# 6. Helper Methods

## 6.1 VideoRecord Class Methods

```python
class VideoRecord(Base):
    # ... columns ...
    
    def append_log(self, msg: str):
        """Append a log message with newline separator"""
        if self.logs:
            self.logs += "\n" + msg
        else:
            self.logs = msg
    
    def get_captions(self) -> dict:
        """Deserialize JSON captions"""
        try:
            return json.loads(self.captions)
        except Exception:
            return {}
    
    def set_captions(self, data: dict):
        """Serialize captions to JSON"""
        self.captions = json.dumps(data)
    
    def get_evaluations(self) -> dict:
        """Deserialize JSON evaluations"""
        try:
            return json.loads(self.evaluations)
        except Exception:
            return {}
    
    def set_evaluations(self, data: dict):
        """Serialize evaluations to JSON"""
        self.evaluations = json.dumps(data)
```

---

# 7. Database Operations

## 7.1 Session Management

```python
def get_db():
    """Dependency injection for FastAPI endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 7.2 Common Queries

### Create Video Record
```python
record = VideoRecord(
    id=video_id,
    filename=file.filename,
    status="uploaded"
)
db.add(record)
db.commit()
```

### Get Video by ID
```python
record = db.query(VideoRecord).filter(VideoRecord.id == video_id).first()
```

### Update Status
```python
record.status = "analyzing"
record.append_log("Running vision model...")
db.commit()
```

### Update Captions
```python
record.set_captions(res["captions"])
record.set_evaluations(res["evaluations"])
db.commit()
```

---

# 8. Storage Locations

## 8.1 Path Resolution

```python
# backend/core/config.py
class Settings(BaseSettings):
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
```

## 8.2 File Storage

- **Database:** `{STORAGE_DIR}/captionforge.db`
- **Videos:** `{STORAGE_DIR}/{video_id}.{ext}`
- **Logs:** Stored in `VideoRecord.logs` column

---

# 9. Considerations

## 9.1 Why SQLite?

| Factor | SQLite | PostgreSQL |
|--------|--------|------------|
| Setup | Zero config | Requires server |
| Deployment | Copy file | External dependency |
| Performance | Good for single-user | Better for concurrent |
| Hackathon fit | ✅ Perfect | Overkill |

## 9.2 Production Recommendations

For production deployment beyond the hackathon:

1. **Migrate to PostgreSQL** for multi-user scenarios
2. **Add indexes** on frequently queried columns
3. **Implement migrations** using Alembic
4. **Add soft deletes** for video records
5. **Separate caption tables** instead of JSON columns

---

# 10. Migration Strategy

## 10.1 Current State (SQLite)

- Single table with JSON columns
- Simple, hackathon-appropriate
- Zero configuration

## 10.2 Production State (PostgreSQL)

```sql
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'idle',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE captions (
    id SERIAL PRIMARY KEY,
    video_id UUID REFERENCES videos(id),
    style VARCHAR(50) NOT NULL,
    caption TEXT NOT NULL,
    accuracy_score DECIMAL(3,2),
    style_score DECIMAL(3,2),
    hallucination_detected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

# 11. Backup & Recovery

## 11.1 Current Approach

- Database stored in temp directory
- Cleared on system restart (expected behavior)
- Videos stored temporarily (tmpfiles.org for serverless)

## 11.2 Production Approach

- Daily PostgreSQL backups
- Object storage (S3) for video files
- Point-in-time recovery capability

---

# Final Sign-off

**Status:** ✅ IMPLEMENTATION ALIGNED

This document accurately reflects the current SQLite + SQLAlchemy implementation used in CaptionForge AI.

