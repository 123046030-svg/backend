from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class MailSettings:
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.mailersend.net")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "MS_F4nSp1@test-65qngkdmzjjlwr12.mlsender.net")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    mail_from: str = os.getenv("MAIL_FROM", "test-65qngkdmzjjlwr12.mlsender.net")
    mail_from_name: str = os.getenv("MAIL_FROM_NAME", "SDUOP")

    default_recipient: Optional[str] = os.getenv("MAIL_DEFAULT_RECIPIENT", "ucarbajal01@gmail.com")

    retry_base_seconds: int = int(os.getenv("MAIL_RETRY_BASE_SECONDS", "60"))
    retry_max_seconds: int = int(os.getenv("MAIL_RETRY_MAX_SECONDS", "3600"))
    poll_interval_seconds: int = int(os.getenv("MAIL_POLL_INTERVAL_SECONDS", "10"))
    max_attempts_default: int = int(os.getenv("MAIL_MAX_ATTEMPTS_DEFAULT", "5"))


mail_settings = MailSettings()