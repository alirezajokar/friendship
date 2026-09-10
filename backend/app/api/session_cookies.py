"""Attach / clear the auth cookie trio on a response."""

from __future__ import annotations

from fastapi import Response

from app.config import settings
from app.core.deps import ACCESS_COOKIE, CSRF_COOKIE, REFRESH_COOKIE, cookie_kwargs
from app.services.auth_service import IssuedSession


def set_session_cookies(response: Response, issued: IssuedSession) -> None:
    response.set_cookie(
        ACCESS_COOKIE, issued.access_token, **cookie_kwargs(settings.access_ttl_seconds)
    )
    response.set_cookie(
        REFRESH_COOKIE, issued.refresh_token, **cookie_kwargs(settings.refresh_ttl_seconds)
    )
    # CSRF cookie is readable by JS (double-submit pattern).
    csrf_kw = cookie_kwargs(settings.refresh_ttl_seconds)
    csrf_kw["httponly"] = False
    response.set_cookie(CSRF_COOKIE, issued.csrf_token, **csrf_kw)


def clear_session_cookies(response: Response) -> None:
    for name in (ACCESS_COOKIE, REFRESH_COOKIE, CSRF_COOKIE):
        response.delete_cookie(name, path="/", domain=settings.cookie_domain or None)
