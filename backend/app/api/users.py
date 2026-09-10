from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DbSession, enforce_csrf
from app.schemas.user import MeOut, ProfileUpdateIn
from app.services.jalali import birthday_gregorian, validate_components

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(enforce_csrf)])


@router.patch("/me", response_model=MeOut)
async def update_me(body: ProfileUpdateIn, user: CurrentUser, db: DbSession) -> MeOut:
    if body.display_name is not None:
        user.display_name = body.display_name.strip()
    if body.email is not None:
        user.email = body.email.strip() or None
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url.strip() or None
    if body.timezone is not None:
        user.timezone = body.timezone.strip() or user.timezone
    if body.birthday is not None:
        b = body.birthday
        validate_components(b.jyear, b.jmonth, b.jday)
        user.birth_jyear = b.jyear
        user.birth_jmonth = b.jmonth
        user.birth_jday = b.jday
        user.birth_gregorian = birthday_gregorian(b.jyear, b.jmonth, b.jday)

    await db.commit()
    await db.refresh(user)
    return MeOut.model_validate(user)
