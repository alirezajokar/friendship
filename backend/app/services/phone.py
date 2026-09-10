"""Phone-number normalization to E.164. Default region is Iran (IR)."""

from __future__ import annotations

import phonenumbers

from app.core.errors import AppError

DEFAULT_REGION = "IR"


def normalize_phone(raw: str, region: str = DEFAULT_REGION) -> str:
    raw = (raw or "").strip()
    if not raw:
        raise AppError(422, "phone_required")
    try:
        parsed = phonenumbers.parse(raw, None if raw.startswith("+") else region)
    except phonenumbers.NumberParseException:
        raise AppError(422, "phone_invalid") from None
    if not phonenumbers.is_valid_number(parsed):
        raise AppError(422, "phone_invalid")
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
