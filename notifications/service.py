from datetime import datetime
from typing import Any, Iterable, Optional, List, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from notifications.config import mail_settings
from notifications.models import EmailOutbox


def _normalize_recipients(recipients: Optional[Iterable[str]]) -> List[str]:
    clean: list[str] = []

    for r in recipients or []:
        if r and str(r).strip():
            clean.append(str(r).strip())

    if not clean and mail_settings.default_recipient:
        clean.append(mail_settings.default_recipient)

    seen = set()
    result = []
    for item in clean:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)

    return result


async def enqueue_email(
    db: AsyncSession,
    recipients: Optional[List[str]],
    subject: str,
    template_name: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    body_html: Optional[str] = None,
    source_module: Optional[str] = None,
    created_by_user_id: Optional[int] = None,
    max_attempts: Optional[int] = None,
) -> EmailOutbox:
    final_recipients = _normalize_recipients(recipients)

    if not final_recipients:
        raise ValueError("No hay recipients válidos ni MAIL_DEFAULT_RECIPIENT configurado.")

    row = EmailOutbox(
        status="PENDING",
        recipients=final_recipients,
        subject=subject,
        template_name=template_name,
        context=context or {},
        body_html=body_html,
        source_module=source_module,
        created_by_user_id=created_by_user_id,
        attempts=0,
        max_attempts=max_attempts or mail_settings.max_attempts_default,
        next_retry_at=datetime.utcnow(),
        last_error=None,
        locked=False,
        locked_at=None,
    )

    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row