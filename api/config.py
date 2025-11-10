
# Importing Libraries
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

# Loading and Validating Environment Variables
class Settings(BaseSettings):
    ENV: str = "dev"
    MAE: int
    PIPE_PATH: Path
    MODEL_FREQ_PATH: Path
    ALLOWED_ORIGINS: str

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env" if not os.getenv("RENDER") else None

settings = Settings()
