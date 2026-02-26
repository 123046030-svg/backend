from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]  # .../app

class Settings(BaseSettings):
    # SMTP
    MAIL_USERNAME: str = "sduop1@geq.net"
    MAIL_PASSWORD: str = "1234567"
    MAIL_FROM: str = "sduop1@geq.net"
    MAIL_FROM_NAME: str = "SDUOP"
    MAIL_SERVER: str = "am11313a.geq.net"
    MAIL_PORT: int = 587

    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    MAIL_TEST_RECIPIENT: str = "scop@queretaro.gob.mx"

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