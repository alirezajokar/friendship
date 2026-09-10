"""Birthday reminder scheduling.

Anniversaries are resolved in the Jalali calendar (see :mod:`app.services.jalali`)
so a fixed Jalali day maps to the correct civil date every year. Offsets are
applied as whole calendar days on the resolved Gregorian date, which keeps the
math immune to time-zone and DST quirks.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ReminderOffset, settings
from app.models import ReminderLog, User
from app.services import friend_service, notification_service
from app.services.jalali import current_jalali_year, resolve_occurrence

log = logging.getLogger("birthday")


@dataclass
class DueWindow:
    occurrence_date: date
    occurrence_jyear: int
    offset: ReminderOffset


def due_windows(
    jmonth: int,
    jday: int,
    tz_name: str,
    now_utc: datetime,
    offsets: list[ReminderOffset] | None = None,
) -> list[DueWindow]:
    """Windows that have *become due* as of ``now_utc`` in the user's timezone.

    A window is due when today (local) equals ``occurrence_date - days_before``
    and the local wall-clock has reached the window's ``hour:minute``. The
    caller is responsible for not firing the same window twice.
    """
    offsets = offsets or settings.offsets
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=UTC)
    try:
        tz = ZoneInfo(tz_name)
    except Exception:  # noqa: BLE001 - bad tz string -> fall back to default
        tz = ZoneInfo(settings.tz_default)

    local_now = now_utc.astimezone(tz)
    today = local_now.date()
    cur_jy = current_jalali_year(today)

    out: list[DueWindow] = []
    for jyear in (cur_jy, cur_jy + 1):
        occ = resolve_occurrence(jmonth, jday, jyear)
        for off in offsets:
            trigger_day = occ - timedelta(days=off.days_before)
            if trigger_day != today:
                continue
            if local_now.timetz().replace(tzinfo=None) < time(off.hour, off.minute):
                continue
            out.append(DueWindow(occ, jyear, off))
    return out


def _days_text(days_before: int) -> str:
    return "امروز" if days_before == 0 else f"{days_before} روز"


async def run_scan(db: AsyncSession, now_utc: datetime | None = None) -> int:
    """Fire any newly-due reminders. Returns the number of notifications sent."""
    now_utc = now_utc or datetime.now(UTC)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=UTC)
    sent = 0

    users = list(
        (
            await db.execute(
                select(User).where(
                    User.is_active.is_(True),
                    User.birth_jmonth.is_not(None),
                    User.birth_jday.is_not(None),
                )
            )
        )
        .scalars()
        .all()
    )

    for bday_user in users:
        windows = due_windows(
            bday_user.birth_jmonth, bday_user.birth_jday, bday_user.timezone, now_utc
        )
        if not windows:
            continue
        friends = await friend_service.list_friends(db, bday_user)
        if not friends:
            continue

        for w in windows:
            for friend in friends:
                if await _claim_log(db, friend.id, bday_user.id, w.occurrence_jyear, w.offset.key):
                    await notification_service.dispatch(
                        db,
                        friend.id,
                        "birthday",
                        {
                            "name": bday_user.display_name or "دوست شما",
                            "user_id": bday_user.id,
                            "days_before": w.offset.days_before,
                            "days_text": _days_text(w.offset.days_before),
                            "date": w.occurrence_date.isoformat(),
                        },
                    )
                    sent += 1
    return sent


async def _claim_log(
    db: AsyncSession, recipient_id: int, bday_user_id: int, jyear: int, offset_key: str
) -> bool:
    """Insert the idempotency row. Returns True if this window was not seen before."""
    db.add(
        ReminderLog(
            recipient_id=recipient_id,
            birthday_user_id=bday_user_id,
            occurrence_jyear=jyear,
            offset_key=offset_key,
        )
    )
    try:
        await db.commit()
        return True
    except IntegrityError:
        await db.rollback()
        return False
