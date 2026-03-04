from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]  # .../app

class Settings(BaseSettings):
    # SMTP - Brevo
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str = "SDUOP"
    MAIL_SERVER: str = "smtp-relay.brevo.com"
    MAIL_PORT: int = 587

    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    MAIL_TEST_RECIPIENT: str = "123046030@upq.edu.mx"

    # Templates
    TEMPLATE_FOLDER: Path = BASE_DIR / "templates"

    # Dev / tests
    MAIL_SUPPRESS_SEND: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()