"""One reusable invite code per user; accepting it sends a friend request."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.errors import AppError
from app.core.security import generate_invite_code
from app.models import Friendship, Invite, User
from app.services import friend_service


async def get_or_create_invite(db: AsyncSession, user: User) -> Invite:
    invite = (
        await db.execute(select(Invite).where(Invite.user_id == user.id))
    ).scalar_one_or_none()
    if invite is None:
        invite = Invite(user_id=user.id, code=generate_invite_code())
        db.add(invite)
        await db.commit()
        await db.refresh(invite)
    return invite


async def regenerate_invite(db: AsyncSession, user: User) -> Invite:
    invite = await get_or_create_invite(db, user)
    invite.code = generate_invite_code()
    await db.commit()
    await db.refresh(invite)
    return invite


def invite_url(code: str) -> str:
    return f"{settings.public_base_url.rstrip('/')}/i/{code}"


async def resolve_inviter(db: AsyncSession, code: str) -> User:
    invite = (
        await db.execute(select(Invite).where(Invite.code == code))
    ).scalar_one_or_none()
    if invite is None:
        raise AppError(404, "invite_not_found")
    inviter = await db.get(User, invite.user_id)
    if inviter is None or not inviter.is_active:
        raise AppError(404, "invite_not_found")
    return inviter


async def accept_invite(db: AsyncSession, code: str, current_user: User) -> Friendship:
    inviter = await resolve_inviter(db, code)
    if inviter.id == current_user.id:
        raise AppError(422, "cannot_invite_self")
    return await friend_service.send_request(db, current_user, inviter.id)
