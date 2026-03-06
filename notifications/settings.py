from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_SYNC: str

    EMAIL_RETRY_MAX_ATTEMPTS: int = 5
    EMAIL_RETRY_BASE_DELAY_SECONDS: int = 30
    EMAIL_RETRY_BACKOFF: int = 2
    EMAIL_RETRY_MAX_DELAY_SECONDS: int = 3600
    EMAIL_RETRY_JITTER_SECONDS: int = 3
    EMAIL_WORKER_POLL_SECONDS: int = 5

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()