import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from notifications.config import mail_settings
from notifications.models import EmailOutbox
from notifications.renderer import render_email
from notifications.smtp_client import send_email_smtp

logger = logging.getLogger(__name__)


def compute_next_retry(attempts: int) -> datetime:
    delay = mail_settings.retry_base_seconds * (2 ** max(0, attempts - 1))
    delay = min(delay, mail_settings.retry_max_seconds)
    return datetime.utcnow() + timedelta(seconds=delay)


async def claim_one_email(db: AsyncSession) -> EmailOutbox | None:
    stmt = (
        select(EmailOutbox)
        .where(
            or_(EmailOutbox.status == "PENDING", EmailOutbox.status == "RETRY"),
            EmailOutbox.locked.is_(False),
            or_(
                EmailOutbox.next_retry_at.is_(None),
                EmailOutbox.next_retry_at <= datetime.utcnow(),
            ),
        )
        .order_by(EmailOutbox.created_at.asc())
        .limit(1)
        .with_for_update(skip_locked=True)
    )

    result = await db.execute(stmt)
    row = result.scalar_one_or_none()

    if not row:
        return None

    row.locked = True
    row.locked_at = datetime.utcnow()
    await db.commit()
    await db.refresh(row)
    return row


async def process_one(db: AsyncSession, row: EmailOutbox) -> None:
    try:
        html = render_email(
            template_name=row.template_name,
            context=row.context,
            body_html=row.body_html,
        )

        await send_email_smtp(
            recipients=row.recipients,
            subject=row.subject,
            html_body=html,
        )

        row.status = "SENT"
        row.sent_at = datetime.utcnow()
        row.last_error = None
        row.locked = False
        row.locked_at = None

        await db.commit()
        logger.info("correo enviado correctamente. outbox_id=%s", row.id)

    except Exception as exc:
        row.attempts += 1
        row.last_error = str(exc)
        row.locked = False
        row.locked_at = None

        if row.attempts >= row.max_attempts:
            row.status = "FAILED"
            row.next_retry_at = None
            logger.exception("correo marcado como failed. outbox_id=%s error=%s", row.id, exc)
        else:
            row.status = "RETRY"
            row.next_retry_at = compute_next_retry(row.attempts)
            logger.exception(
                "correo marcado para retry. outbox_id=%s attempts=%s next_retry_at=%s error=%s",
                row.id,
                row.attempts,
                row.next_retry_at,
                exc,
            )

        await db.commit()


async def run_email_worker(session_factory: async_sessionmaker[AsyncSession]) -> None:
    logger.info("iniciando email worker...")

    while True:
        processed = False

        try:
            async with session_factory() as db:
                row = await claim_one_email(db)
                if row:
                    processed = True
                    await process_one(db, row)
        except Exception:
            logger.exception("error general en worker de correos")

        if not processed:
            await asyncio.sleep(mail_settings.poll_interval_seconds)