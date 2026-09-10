"""Jalali (Solar Hijri) calendar helpers.

`persiantools` is the single source of truth for calendar conversion across the
whole backend. Birthday anniversaries are computed in the Jalali calendar so
that a fixed Jalali day (e.g. "11 Tir") always resolves to the civil date the
user actually celebrates — the naive "reuse the Gregorian month/day" approach
drifts by a day roughly one year in four because Jalali and Gregorian leap
years do not line up.
"""

from __future__ import annotations

from datetime import date

from persiantools.jdatetime import JalaliDate

from app.core.errors import AppError

ESFAND = 12


def is_leap(jyear: int) -> bool:
    return JalaliDate.is_leap(jyear)


def jalali_month_length(jyear: int, jmonth: int) -> int:
    if jmonth <= 6:
        return 31
    if jmonth <= 11:
        return 30
    return 30 if is_leap(jyear) else 29


def to_gregorian(jyear: int, jmonth: int, jday: int) -> date:
    return JalaliDate(jyear, jmonth, jday).to_gregorian()


def to_jalali(d: date) -> tuple[int, int, int]:
    j = JalaliDate(d)
    return j.year, j.month, j.day


def current_jalali_year(today: date) -> int:
    return JalaliDate(today).year


def validate_components(jyear: int | None, jmonth: int, jday: int) -> None:
    if not 1 <= jmonth <= 12:
        raise AppError(422, "birthday_invalid")
    # Use a leap year as the yardstick when the year is unknown, so 30 Esfand is
    # accepted; the year-specific fallback happens at resolve time.
    ref_year = jyear if jyear is not None else 1403
    if not 1 <= jday <= jalali_month_length(ref_year, jmonth):
        raise AppError(422, "birthday_invalid")
    if jyear is not None and not (1200 <= jyear <= 1500):
        raise AppError(422, "birthday_invalid")


def resolve_occurrence(jmonth: int, jday: int, jyear: int) -> date:
    """Gregorian date of (jyear, jmonth, jday), with the 30-Esfand fallback.

    30 Esfand exists only in Jalali leap years; in a common year the birthday
    is observed on 29 Esfand.
    """
    day = jday
    max_day = jalali_month_length(jyear, jmonth)
    if day > max_day:
        day = max_day
    return to_gregorian(jyear, jmonth, day)


def birthday_gregorian(jyear: int | None, jmonth: int, jday: int) -> date | None:
    """Derived Gregorian DOB for display/age. None when the birth year is unknown."""
    if jyear is None:
        return None
    return resolve_occurrence(jmonth, jday, jyear)
