import asyncio
import logging
from typing import Optional
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

    logger.warning(
        "[worker.compute_next_retry] attempts=%s retry_base_seconds=%s retry_max_seconds=%s delay=%s",
        attempts,
        mail_settings.retry_base_seconds,
        mail_settings.retry_max_seconds,
        delay,
    )

    return datetime.utcnow() + timedelta(seconds=delay)


def is_permanent_email_error(exc: Exception) -> bool:
    text = str(exc).lower()

    permanent_patterns = [
        "from.email domain must be verified",
        "domain must be verified",
        "#ms42207",
        "invalid from",
        "sender not authorized",
        "not allowed to send",
    ]

    return any(pattern in text for pattern in permanent_patterns)


async def claim_one_email(db: AsyncSession) -> Optional[EmailOutbox]:
    logger.warning("[worker.claim_one_email] buscando correo pendiente o retry")

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
        logger.warning("[worker.claim_one_email] no se encontró correo elegible")
        return None

    logger.warning(
        "[worker.claim_one_email] correo encontrado | outbox_id=%s status=%s attempts=%s max_attempts=%s next_retry_at=%s recipients=%s subject=%s",
        row.id,
        row.status,
        row.attempts,
        row.max_attempts,
        row.next_retry_at,
        row.recipients,
        row.subject,
    )

    row.locked = True
    row.locked_at = datetime.utcnow()
    await db.commit()
    await db.refresh(row)

    logger.warning(
        "[worker.claim_one_email] correo bloqueado | outbox_id=%s locked=%s locked_at=%s",
        row.id,
        row.locked,
        row.locked_at,
    )

    return row


async def process_one(db: AsyncSession, row: EmailOutbox) -> None:
    logger.warning(
        "[worker.process_one] iniciando procesamiento | outbox_id=%s status=%s attempts=%s max_attempts=%s template_name=%s recipients=%s subject=%s",
        row.id,
        row.status,
        row.attempts,
        row.max_attempts,
        row.template_name,
        row.recipients,
        row.subject,
    )

    try:
        html = render_email(
            template_name=row.template_name,
            context=row.context,
            body_html=row.body_html,
        )

        logger.warning(
            "[worker.process_one] html renderizado | outbox_id=%s html_len=%s has_context=%s",
            row.id,
            len(html or ""),
            bool(row.context),
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

        logger.warning(
            "[worker.process_one] correo enviado correctamente | outbox_id=%s sent_at=%s",
            row.id,
            row.sent_at,
        )

    except Exception as exc:
        row.attempts += 1
        row.last_error = str(exc)
        row.locked = False
        row.locked_at = None

        logger.warning(
            "[worker.process_one] excepción capturada | outbox_id=%s attempts=%s max_attempts=%s error=%r",
            row.id,
            row.attempts,
            row.max_attempts,
            exc,
        )

        if is_permanent_email_error(exc):
            row.status = "FAILED"
            row.next_retry_at = None

            logger.warning(
                "[worker.process_one] error permanente detectado, se marca FAILED | outbox_id=%s error=%r",
                row.id,
                exc,
            )

        elif row.attempts >= row.max_attempts:
            row.status = "FAILED"
            row.next_retry_at = None

            logger.warning(
                "[worker.process_one] max_attempts alcanzado, se marca FAILED | outbox_id=%s attempts=%s error=%r",
                row.id,
                row.attempts,
                exc,
            )

        else:
            row.status = "RETRY"
            row.next_retry_at = compute_next_retry(row.attempts)

            logger.warning(
                "[worker.process_one] correo marcado para RETRY | outbox_id=%s attempts=%s next_retry_at=%s error=%r",
                row.id,
                row.attempts,
                row.next_retry_at,
                exc,
            )

        await db.commit()

        logger.exception(
            "[worker.process_one] commit realizado después del error | outbox_id=%s status=%s last_error=%s",
            row.id,
            row.status,
            row.last_error,
        )


async def run_email_worker(session_factory: async_sessionmaker) -> None:
    logger.warning(
        "[worker.run_email_worker] iniciando worker | poll_interval_seconds=%s",
        mail_settings.poll_interval_seconds,
    )

    while True:
        processed = False

        try:
            async with session_factory() as db:
                row = await claim_one_email(db)
                if row:
                    processed = True
                    await process_one(db, row)
        except Exception:
            logger.exception("[worker.run_email_worker] error general en worker")

        if not processed:
            logger.warning(
                "[worker.run_email_worker] sin correos para procesar, sleep=%s",
                mail_settings.poll_interval_seconds,
            )
            await asyncio.sleep(mail_settings.poll_interval_seconds)