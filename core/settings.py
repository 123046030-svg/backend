from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]  # .../app

class Settings(BaseSettings):
    # SMTP
    MAIL_USERNAME: str = "smtp-relay.brevo.com"
    MAIL_PASSWORD: str = "bskx2ZlnEqKRn4c"
    MAIL_FROM: str = "a38dfa001@smtp-brevo.com"
    MAIL_FROM_NAME: str = "SDUOP"
    MAIL_SERVER: str = "smtp-relay.brevo.com"
    MAIL_PORT: int = 587

    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    MAIL_TEST_RECIPIENT: str = "reginacorteees@gmail.com"

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