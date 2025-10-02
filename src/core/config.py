from pydantic_settings import BaseSettings
import os
from typing import List, Dict

class Settings(BaseSettings):
    API_V1_PREFIX: str = "/api/v1"
    APP_NAME: str = "FastAPI Image Processor"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Configurações de Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    LOG_FILE_MAX_SIZE: int = int(os.getenv("LOG_FILE_MAX_SIZE", "10485760"))  # 10MB
    LOG_FILE_BACKUP_COUNT: int = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))
    
    # Configurações de ONNX Runtime
    ONNX_PROVIDERS: List[str] = ["CPUExecutionProvider"]

    class Config:
        env_file = ".env"

settings = Settings()
