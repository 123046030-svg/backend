from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]  # .../backend
ENV_PATH = BASE_DIR / ".env"

# (Opcional) fallback si INSISTES en guardarlo en __pycache__
ALT_ENV = BASE_DIR / "__pycache__" / ".env"
if not ENV_PATH.exists() and ALT_ENV.exists():
    ENV_PATH = ALT_ENV

class Settings(BaseSettings):
    # SMTP (sin defaults)
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

    MAIL_TEST_RECIPIENT: str | None = None

    TEMPLATE_FOLDER: Path = BASE_DIR / "templates"
    MAIL_SUPPRESS_SEND: bool = False

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()