"""Request-scoped dependencies: DB session, current user, CSRF guard."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.errors import AppError
from app.core.security import csrf_matches, decode_access_token
from app.db import get_db
from app.models import User

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "x-csrf-token"
_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def enforce_csrf(request: Request) -> None:
    """Double-submit cookie check for state-changing requests."""
    if request.method in _SAFE_METHODS:
        return
    cookie = request.cookies.get(CSRF_COOKIE, "")
    header = request.headers.get(CSRF_HEADER, "")
    if not csrf_matches(cookie, header):
        raise AppError(403, "csrf_failed")


async def get_current_user(request: Request, db: DbSession) -> User:
    token = request.cookies.get(ACCESS_COOKIE)
    user_id = decode_access_token(token) if token else None
    if user_id is None:
        raise AppError(401, "not_authenticated")
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise AppError(401, "not_authenticated")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def cookie_kwargs(max_age: int) -> dict:
    """Shared attributes for auth cookies."""
    kw = {
        "httponly": True,
        "secure": settings.cookie_secure,
        "samesite": "lax",
        "max_age": max_age,
        "path": "/",
    }
    if settings.cookie_domain:
        kw["domain"] = settings.cookie_domain
    return kw
