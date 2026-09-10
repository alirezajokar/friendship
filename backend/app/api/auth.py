from __future__ import annotations

from fastapi import APIRouter, Request, Response

from app.api.session_cookies import clear_session_cookies, set_session_cookies
from app.core import ratelimit
from app.core.deps import REFRESH_COOKIE, CurrentUser, DbSession
from app.core.errors import AppError
from app.schemas.auth import OtpRequestIn, OtpRequestOut, OtpVerifyIn, SessionOut
from app.schemas.user import MeOut
from app.services import auth_service, otp_service
from app.services.phone import normalize_phone

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/request", response_model=OtpRequestOut)
async def otp_request(body: OtpRequestIn, request: Request, db: DbSession) -> OtpRequestOut:
    ip = request.client.host if request.client else "unknown"
    if not ratelimit.hit(f"otp:ip:{ip}", 30, 3600):
        raise AppError(429, "otp_rate_limited")
    phone = normalize_phone(body.phone)
    result = await otp_service.request_otp(db, phone)
    return OtpRequestOut(**result)


@router.post("/otp/verify", response_model=SessionOut)
async def otp_verify(body: OtpVerifyIn, response: Response, db: DbSession) -> SessionOut:
    phone = normalize_phone(body.phone)
    await otp_service.verify_otp(db, phone, body.code)
    user, is_new = await auth_service.get_or_create_user(db, phone)
    issued = await auth_service.issue_session(db, user.id)
    set_session_cookies(response, issued)
    return SessionOut(is_new=is_new, profile_completed=user.profile_completed)


@router.post("/refresh", status_code=204)
async def refresh(request: Request, response: Response, db: DbSession) -> Response:
    raw = request.cookies.get(REFRESH_COOKIE)
    if not raw:
        raise AppError(401, "no_refresh")
    issued = await auth_service.rotate_session(db, raw)
    set_session_cookies(response, issued)
    response.status_code = 204
    return response


@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response, db: DbSession) -> Response:
    raw = request.cookies.get(REFRESH_COOKIE)
    if raw:
        await auth_service.revoke_session(db, raw)
    clear_session_cookies(response)
    response.status_code = 204
    return response


@router.get("/me", response_model=MeOut)
async def me(user: CurrentUser) -> MeOut:
    return MeOut.model_validate(user)
