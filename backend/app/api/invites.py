from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DbSession, enforce_csrf
from app.schemas.invite import InviteAcceptOut, InviteOut, InvitePreviewOut
from app.schemas.user import PublicUserOut
from app.services import invite_service, notification_service

router = APIRouter(tags=["invites"])


@router.get("/invites/me", response_model=InviteOut)
async def my_invite(user: CurrentUser, db: DbSession) -> InviteOut:
    invite = await invite_service.get_or_create_invite(db, user)
    return InviteOut(code=invite.code, url=invite_service.invite_url(invite.code))


@router.post("/invites/regenerate", response_model=InviteOut, dependencies=[Depends(enforce_csrf)])
async def regenerate(user: CurrentUser, db: DbSession) -> InviteOut:
    invite = await invite_service.regenerate_invite(db, user)
    return InviteOut(code=invite.code, url=invite_service.invite_url(invite.code))


@router.get("/i/{code}", response_model=InvitePreviewOut)
async def preview(code: str, db: DbSession) -> InvitePreviewOut:
    inviter = await invite_service.resolve_inviter(db, code)
    return InvitePreviewOut(inviter=PublicUserOut.model_validate(inviter))


@router.post(
    "/invites/{code}/accept",
    response_model=InviteAcceptOut,
    dependencies=[Depends(enforce_csrf)],
)
async def accept(code: str, user: CurrentUser, db: DbSession) -> InviteAcceptOut:
    edge = await invite_service.accept_invite(db, code, user)
    inviter = await invite_service.resolve_inviter(db, code)
    if edge.status.value == "pending":
        await notification_service.dispatch(
            db, inviter.id, "friend_request", {"name": user.display_name or "کاربر جدید"}
        )
    return InviteAcceptOut(status=edge.status.value, inviter=PublicUserOut.model_validate(inviter))
