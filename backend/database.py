import json
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from core.config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class VideoRecord(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="idle")
    logs = Column(Text, default="")
    captions = Column(Text, default="{}")       # JSON string
    evaluations = Column(Text, default="{}")    # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def append_log(self, msg: str):
        if self.logs:
            self.logs += "\n" + msg
        else:
            self.logs = msg

    def get_captions(self):
        try:
            return json.loads(self.captions)
        except Exception:
            return {}

    def set_captions(self, data: dict):
        self.captions = json.dumps(data)

    def get_evaluations(self):
        try:
            return json.loads(self.evaluations)
        except Exception:
            return {}

    def set_evaluations(self, data: dict):
        self.evaluations = json.dumps(data)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
