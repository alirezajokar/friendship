"""One-time-code request + verification.

Codes are single-use, short-lived, attempt-capped, and stored only as an HMAC
hash. Send rate is limited per phone (see :mod:`app.core.ratelimit`); the router
adds a per-IP limit on top.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core import ratelimit
from app.core.errors import AppError
from app.core.security import generate_otp, hash_otp
from app.core.security import verify_otp as _verify_hash
from app.models import OtpCode
from app.providers.sms import get_sms_provider

log = logging.getLogger("otp")


async def request_otp(db: AsyncSession, phone: str) -> dict:
    if not ratelimit.hit(f"otp:cooldown:{phone}", 1, settings.otp_resend_cooldown_seconds):
        wait = ratelimit.seconds_until_next(
            f"otp:cooldown:{phone}", 1, settings.otp_resend_cooldown_seconds
        )
        raise AppError(429, f"otp_cooldown:{wait}")
    if not ratelimit.hit(f"otp:hour:{phone}", settings.otp_max_per_hour, 3600):
        raise AppError(429, "otp_rate_limited")

    await db.execute(delete(OtpCode).where(OtpCode.phone == phone, OtpCode.consumed_at.is_(None)))

    code = generate_otp()
    db.add(
        OtpCode(
            phone=phone,
            code_hash=hash_otp(phone, code),
            expires_at=datetime.now(UTC) + timedelta(seconds=settings.otp_ttl_seconds),
        )
    )
    await db.commit()

    text = f"کد ورود شما به اپ دوستی: {code}\nاعتبار: {settings.otp_ttl_seconds // 60} دقیقه"
    try:
        await get_sms_provider().send(phone, text)
    except Exception:  # noqa: BLE001 - never leak provider errors to the caller
        log.exception("SMS send failed for %s", phone)

    return {"resend_cooldown_seconds": settings.otp_resend_cooldown_seconds}


async def verify_otp(db: AsyncSession, phone: str, code: str) -> bool:
    row = (
        await db.execute(
            select(OtpCode)
            .where(OtpCode.phone == phone, OtpCode.consumed_at.is_(None))
            .order_by(OtpCode.id.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    now = datetime.now(UTC)
    if row is None or row.expires_at < now:
        raise AppError(400, "otp_invalid_or_expired")
    if row.attempts >= settings.otp_max_attempts:
        raise AppError(429, "otp_too_many_attempts")

    if not _verify_hash(phone, code, row.code_hash):
        row.attempts += 1
        await db.commit()
        raise AppError(400, "otp_invalid")

    row.consumed_at = now
    await db.commit()
    return True
