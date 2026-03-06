# modules/notifications/service.py
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
from .models import EmailOutbox
from core.settings import settings
from services.mailer import Mailer

def utcnow():
    return datetime.now(timezone.utc)

def compute_next_retry(attempt: int) -> datetime:
    # exponential backoff con jitter
    base = settings.EMAIL_RETRY_BASE_DELAY_SECONDS
    backoff = settings.EMAIL_RETRY_BACKOFF
    max_delay = settings.EMAIL_RETRY_MAX_DELAY_SECONDS
    jitter = settings.EMAIL_RETRY_JITTER_SECONDS

    delay = min(int(base * (backoff ** max(0, attempt - 1))), max_delay)
    delay += random.randint(0, max(0, jitter))
    return utcnow() + timedelta(seconds=delay)

def is_transient_error(exc: Exception) -> bool:
    # Ajusta a tus excepciones típicas: ConnectionErrors, TimeoutError, etc.
    name = type(exc).__name__
    return name in {"ConnectionErrors", "TimeoutError", "OSError"}

async def enqueue_email(
    db: AsyncSession,
    *,
    recipients: list[str],
    subject: str,
    template_name: Optional[str],
    context: Optional[Dict[str, Any]],
    body_html: Optional[str],
    source_module: Optional[str],
    created_by_user_id: Optional[int],
) -> EmailOutbox:
    row = EmailOutbox(
        recipients=recipients,
        subject=subject,
        template_name=template_name,
        context=context,
        body_html=body_html,
        source_module=source_module,
        created_by_user_id=created_by_user_id,
        max_attempts=settings.EMAIL_RETRY_MAX_ATTEMPTS,
        status="PENDING",
        next_retry_at=utcnow(),  # listo para enviar
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row

async def try_send_one(db: AsyncSession, mailer: Mailer, row: EmailOutbox) -> None:
    try:
        # marca como SENDING
        row.status = "SENDING"
        await db.commit()

        if row.template_name:
            await mailer.send_template(
                subject=row.subject,
                recipients=row.recipients,
                template_name=row.template_name,
                context=row.context or {},
                background_tasks=None,
            )
        else:
            await mailer.send_html(
                subject=row.subject,
                recipients=row.recipients,
                html=row.body_html or "",
                background_tasks=None,
            )

        row.status = "SENT"
        row.sent_at = utcnow()
        row.last_error = None
        await db.commit()

    except Exception as e:
        row.attempts += 1
        row.last_error = f"{type(e).__name__}: {e}"

        retry_allowed = row.attempts < row.max_attempts
        if settings.EMAIL_RETRY_ONLY_TRANSIENT and not is_transient_error(e):
            retry_allowed = False

        if retry_allowed:
            row.status = "RETRY"
            row.next_retry_at = compute_next_retry(row.attempts)
        else:
            row.status = "FAILED"

        await db.commit()