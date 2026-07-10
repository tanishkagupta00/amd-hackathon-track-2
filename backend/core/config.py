import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CaptionForge AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Check if we are running in Windows or container to resolve paths
    IS_WINDOWS: bool = os.name == 'nt'
    
    # Store dynamic databases and uploads in TEMP for Windows, or standard storage for docker
    TEMP_DIR: str = os.environ.get("TEMP", "/tmp")
    
    @property
    def STORAGE_DIR(self) -> str:
        if self.IS_WINDOWS:
            d = os.path.join(self.TEMP_DIR, "captionforge_storage")
        else:
            d = "/app/storage"
        os.makedirs(d, exist_ok=True)
        return d

    @property
    def DATABASE_URL(self) -> str:
        db_path = os.path.join(self.STORAGE_DIR, "captionforge.db")
        return f"sqlite:///{db_path}"

    class Config:
        case_sensitive = True

settings = Settings()
