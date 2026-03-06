# modules/notifications/worker.py
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import EmailOutbox
from .service import try_send_one, utcnow
from services.mailer import Mailer
from core.db import async_session_maker  # tu factory real
from notifications.settings import settings

async def fetch_due(db: AsyncSession) -> EmailOutbox | None:
    q = (
        select(EmailOutbox)
        .where(EmailOutbox.status.in_(["PENDING", "RETRY"]))
        .where(EmailOutbox.next_retry_at <= utcnow())
        .order_by(EmailOutbox.id.asc())
        .limit(1)
    )
    res = await db.execute(q)
    return res.scalar_one_or_none()

async def run_worker():
    mailer = Mailer()
    while True:
        async with async_session_maker() as db:
            row = await fetch_due(db)
            if row:
                await try_send_one(db, mailer, row)
        await asyncio.sleep(settings.EMAIL_WORKER_POLL_SECONDS)

if __name__ == "__main__":
    asyncio.run(run_worker())