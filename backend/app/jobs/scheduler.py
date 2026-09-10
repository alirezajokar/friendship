from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.jobs.birthday_reminders import run_once

log = logging.getLogger("scheduler")


def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    # Hourly at minute 0. Each birthday user is evaluated in their own timezone,
    # so an hourly UTC tick is enough to catch every local reminder window.
    scheduler.add_job(
        run_once,
        CronTrigger(minute=0),
        id="birthday_reminders",
        max_instances=1,
        coalesce=True,
    )
    return scheduler
