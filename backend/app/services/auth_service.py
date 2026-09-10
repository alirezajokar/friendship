"""User bootstrap + rotating refresh-token sessions.

Session model (see the design doc): a short-lived access JWT plus an opaque
refresh token stored as a SHA-256 hash. Every refresh rotates the token within
its *family*; presenting an already-rotated token means it leaked, so the whole
family is revoked. Sliding expiry extends the window on each use up to a hard
absolute cap.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    generate_csrf_token,
    generate_refresh_token,
    hash_token,
    new_family_id,
)
from app.models import NotificationPref, SessionToken, User


@dataclass
class IssuedSession:
    user_id: int
    access_token: str
    refresh_token: str
    csrf_token: str


async def get_or_create_user(db: AsyncSession, phone: str) -> tuple[User, bool]:
    user = (
        await db.execute(select(User).where(User.phone == phone))
    ).scalar_one_or_none()
    if user is not None:
        return user, False
    user = User(phone=phone)
    db.add(user)
    await db.flush()
    db.add(NotificationPref(user_id=user.id))
    await db.commit()
    await db.refresh(user)
    return user, True


async def issue_session(db: AsyncSession, user_id: int) -> IssuedSession:
    now = datetime.now(UTC)
    raw_refresh = generate_refresh_token()
    db.add(
        SessionToken(
            user_id=user_id,
            family_id=new_family_id(),
            token_hash=hash_token(raw_refresh),
            expires_at=now + timedelta(seconds=settings.refresh_ttl_seconds),
            absolute_expires_at=now + timedelta(seconds=settings.refresh_absolute_ttl_seconds),
        )
    )
    await db.commit()
    return IssuedSession(
        user_id=user_id,
        access_token=create_access_token(user_id),
        refresh_token=raw_refresh,
        csrf_token=generate_csrf_token(),
    )


async def _revoke_family(db: AsyncSession, family_id: str) -> None:
    await db.execute(
        update(SessionToken)
        .where(SessionToken.family_id == family_id, SessionToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )


async def rotate_session(db: AsyncSession, raw_refresh: str) -> IssuedSession:
    now = datetime.now(UTC)
    row = (
        await db.execute(
            select(SessionToken).where(SessionToken.token_hash == hash_token(raw_refresh))
        )
    ).scalar_one_or_none()

    if row is None or row.revoked_at is not None:
        raise AppError(401, "invalid_refresh")

    if row.rotated_at is not None:
        # Token reuse -> treat the whole family as compromised.
        await _revoke_family(db, row.family_id)
        await db.commit()
        raise AppError(401, "refresh_reused")

    if row.expires_at < now or row.absolute_expires_at < now:
        raise AppError(401, "refresh_expired")

    row.rotated_at = now
    raw_new = generate_refresh_token()
    db.add(
        SessionToken(
            user_id=row.user_id,
            family_id=row.family_id,
            token_hash=hash_token(raw_new),
            expires_at=now + timedelta(seconds=settings.refresh_ttl_seconds),
            absolute_expires_at=row.absolute_expires_at,  # hard cap is preserved
        )
    )
    await db.commit()
    return IssuedSession(
        user_id=row.user_id,
        access_token=create_access_token(row.user_id),
        refresh_token=raw_new,
        csrf_token=generate_csrf_token(),
    )


async def revoke_session(db: AsyncSession, raw_refresh: str) -> None:
    row = (
        await db.execute(
            select(SessionToken).where(SessionToken.token_hash == hash_token(raw_refresh))
        )
    ).scalar_one_or_none()
    if row is not None:
        await _revoke_family(db, row.family_id)
        await db.commit()
