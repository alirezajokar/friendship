"""Token minting, OTP hashing, and other crypto helpers.

Nothing here touches the database. All comparisons of secret material use
constant-time equality.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.config import settings

_ALGO = "HS256"


# --- OTP ---------------------------------------------------------------------
def generate_otp(length: int | None = None) -> str:
    n = length or settings.otp_length
    return "".join(secrets.choice("0123456789") for _ in range(n))


def hash_otp(phone: str, code: str) -> str:
    msg = f"{phone}:{code}".encode()
    return hmac.new(settings.otp_hmac_secret.encode(), msg, hashlib.sha256).hexdigest()


def verify_otp(phone: str, code: str, code_hash: str) -> bool:
    return hmac.compare_digest(hash_otp(phone, code), code_hash)


# --- Access token (JWT, short-lived) ---------------------------------------
def create_access_token(user_id: int) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=settings.access_ttl_seconds)).timestamp()),
        "typ": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGO)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[_ALGO])
    except JWTError:
        return None
    if payload.get("typ") != "access":
        return None
    try:
        return int(payload["sub"])
    except (KeyError, ValueError):
        return None


# --- Refresh token (opaque, stored hashed) --------------------------------
def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def new_family_id() -> str:
    return secrets.token_urlsafe(32)


# --- Misc ----------------------------------------------------------------
def generate_invite_code() -> str:
    return secrets.token_urlsafe(16)


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def csrf_matches(a: str, b: str) -> bool:
    return bool(a) and bool(b) and hmac.compare_digest(a, b)
