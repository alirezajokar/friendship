"""Background worker.

    python -m app.worker              # run the scheduler forever (hourly scan)
    python -m app.worker --run-now    # run one scan and exit (handy in tests / demos)
    python -m app.worker --run-now --base-now 2026-07-01T09:05:00+03:30
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")


async def _run_now(base_now: datetime | None) -> None:
    from app.jobs.birthday_reminders import run_once

    sent = await run_once(base_now)
    logging.getLogger("worker").info("scan complete; %d reminder(s) sent", sent)


async def _serve_forever() -> None:
    from app.jobs.scheduler import build_scheduler

    scheduler = build_scheduler()
    scheduler.start()
    logging.getLogger("worker").info("scheduler started")
    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown(wait=False)


def main() -> None:
    parser = argparse.ArgumentParser(prog="app.worker")
    parser.add_argument("--run-now", action="store_true", help="run one scan and exit")
    parser.add_argument("--base-now", help="ISO datetime to use as 'now' (implies --run-now)")
    args = parser.parse_args()

    base_now = datetime.fromisoformat(args.base_now) if args.base_now else None
    if args.run_now or base_now is not None:
        asyncio.run(_run_now(base_now))
    else:
        asyncio.run(_serve_forever())


if __name__ == "__main__":
    main()
