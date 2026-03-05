from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[1]  # /var/www/html/backend
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str = "SDUOP"
    MAIL_SERVER: str
    MAIL_PORT: int = 587

    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    MAIL_TEST_RECIPIENT: Optional[str] = None

    TEMPLATE_FOLDER: Path = BASE_DIR / "templates"
    MAIL_SUPPRESS_SEND: bool = False

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()