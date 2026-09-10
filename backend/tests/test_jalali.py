"""Jalali conversion + anniversary resolution.

The core risk (see the design doc): a fixed Jalali day maps to a *different*
Gregorian date across years because Jalali and Gregorian leap years don't align.
"""

from datetime import date

import pytest

from app.core.errors import AppError
from app.services.jalali import (
    is_leap,
    jalali_month_length,
    resolve_occurrence,
    to_gregorian,
    validate_components,
)


def test_known_conversion():
    assert to_gregorian(1376, 4, 11) == date(1997, 7, 2)


def test_anniversary_drifts_around_jalali_leap_year():
    # 1403 is a Jalali leap year -> "11 Tir" lands on 1 July that Gregorian year,
    # not the usual 2 July. The naive "reuse 07-02 every year" approach is wrong here.
    assert is_leap(1403) is True
    assert resolve_occurrence(4, 11, 1403) == date(2024, 7, 1)
    assert resolve_occurrence(4, 11, 1404) == date(2025, 7, 2)
    assert resolve_occurrence(4, 11, 1400) == date(2021, 7, 2)


def test_30_esfand_falls_back_to_29_in_common_year():
    assert is_leap(1403) is True and jalali_month_length(1403, 12) == 30
    assert is_leap(1404) is False and jalali_month_length(1404, 12) == 29
    # Born 30 Esfand (only exists in leap years) -> observed on 29 Esfand otherwise.
    assert resolve_occurrence(12, 30, 1403) == to_gregorian(1403, 12, 30)
    assert resolve_occurrence(12, 30, 1404) == to_gregorian(1404, 12, 29)


def test_feb_29_equivalent_is_a_non_issue_with_jalali_anchor():
    # 10 Esfand 1358 == 29 Feb 1980. Anchored in Jalali, every year resolves fine.
    assert to_gregorian(1358, 12, 10) == date(1980, 2, 29)
    for jy in range(1400, 1410):
        d = resolve_occurrence(12, 10, jy)
        assert isinstance(d, date)


def test_validate_components_rejects_bad_input():
    with pytest.raises(AppError):
        validate_components(None, 13, 1)
    with pytest.raises(AppError):
        validate_components(1404, 12, 30)  # 1404 common year has no 30 Esfand
    with pytest.raises(AppError):
        validate_components(1000, 1, 1)
    validate_components(None, 12, 30)  # year unknown -> accepted (leap yardstick)
    validate_components(1403, 12, 30)  # leap year -> ok
