import asyncio
import logging

from core.db import async_session_maker
from notifications.worker import run_email_worker

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

if __name__ == "__main__":
    asyncio.run(run_email_worker(async_session_maker))