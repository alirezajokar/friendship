"""Job entrypoint: open a session, run one birthday-reminder scan."""

from __future__ import annotations

import logging
from datetime import datetime

from app.db import SessionLocal
from app.services import birthday_service

log = logging.getLogger("jobs.birthday")


async def run_once(now: datetime | None = None) -> int:
    async with SessionLocal() as db:
        sent = await birthday_service.run_scan(db, now)
    if sent:
        log.info("birthday reminders sent: %d", sent)
    return sent
