"""Birthday reminder windows + idempotent scan."""

from datetime import UTC, datetime

import pytest

from app.config import ReminderOffset
from app.models import Friendship, FriendshipStatus, User
from app.services import birthday_service
from app.services.birthday_service import due_windows, run_scan

OFFSETS = [
    ReminderOffset(7, 9, 0),
    ReminderOffset(3, 9, 0),
    ReminderOffset(1, 21, 0),
    ReminderOffset(0, 9, 0),
]


def _at(y, m, d, hh=9, mm=30):
    # Tehran is a fixed +03:30 offset (no DST since 2022); express as UTC.
    return datetime(y, m, d, hh, mm, tzinfo=UTC) - _tehran_offset()


def _tehran_offset():
    from datetime import timedelta

    return timedelta(hours=3, minutes=30)


def test_day_of_window_fires_after_local_9am():
    # "11 Tir 1376"; the 2025 occurrence is 2 July 2025.
    wins = due_windows(4, 11, "Asia/Tehran", _at(2025, 7, 2, 9, 5), OFFSETS)
    keys = {w.offset.key for w in wins}
    assert "d0" in keys
    assert all(w.occurrence_jyear == 1404 for w in wins if w.offset.key == "d0")


def test_day_of_window_not_yet_due_before_local_time():
    wins = due_windows(4, 11, "Asia/Tehran", _at(2025, 7, 2, 8, 0), OFFSETS)
    assert "d0" not in {w.offset.key for w in wins}


def test_seven_day_window_uses_leap_shifted_date():
    # 2024 occurrence of 11 Tir is 1 July (Jalali leap 1403) -> -7d window is 24 June.
    wins = due_windows(4, 11, "Asia/Tehran", _at(2024, 6, 24, 9, 1), OFFSETS)
    assert "d7" in {w.offset.key for w in wins}
    wrong = due_windows(4, 11, "Asia/Tehran", _at(2024, 6, 25, 9, 1), OFFSETS)
    assert "d7" not in {w.offset.key for w in wrong}


def test_nowruz_crossing_offset_lands_in_previous_jalali_year():
    # Birthday 2 Farvardin -> occurrence ~22 March; -7d window is mid-March,
    # which is still the *previous* Jalali year. Must still be detected.
    wins = due_windows(1, 2, "Asia/Tehran", _at(2025, 3, 15, 9, 5), OFFSETS)
    assert "d7" in {w.offset.key for w in wins}


@pytest.mark.asyncio
async def test_run_scan_is_idempotent(db_session):
    bday = User(phone="+15550001", display_name="Bday", timezone="Asia/Tehran",
                birth_jmonth=4, birth_jday=11)
    friend = User(phone="+15550002", display_name="Friend")
    db_session.add_all([bday, friend])
    await db_session.flush()
    db_session.add(
        Friendship(requester_id=friend.id, addressee_id=bday.id,
                   status=FriendshipStatus.accepted)
    )
    await db_session.commit()

    monkeynow = _at(2025, 7, 2, 9, 10)
    # keep the module using our 4 canonical offsets regardless of env
    birthday_service.settings.reminder_offsets = "7:09:00,3:09:00,1:21:00,0:09:00"

    sent_first = await run_scan(db_session, monkeynow)
    sent_again = await run_scan(db_session, monkeynow)
    assert sent_first >= 1
    assert sent_again == 0
