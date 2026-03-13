from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text, Boolean
from typing import Optional
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from sqlalchemy.orm import Mapped, mapped_column

from core.db_base import Base


class EmailOutbox(Base):
    __tablename__ = "email_outbox"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
    )  # PENDING | RETRY | SENT | FAILED

    recipients: Mapped[list] = mapped_column(MySQLJSON, nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)

    template_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    context: Mapped[Optional[dict]] = mapped_column(MySQLJSON, nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source_module: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)