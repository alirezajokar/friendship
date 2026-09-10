from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DbSession, enforce_csrf
from app.models import User
from app.schemas.friend import FriendRequestOut, RespondIn
from app.schemas.user import PublicUserOut
from app.services import friend_service, notification_service

router = APIRouter(prefix="/friends", tags=["friends"], dependencies=[Depends(enforce_csrf)])


@router.get("", response_model=list[PublicUserOut])
async def list_friends(user: CurrentUser, db: DbSession) -> list[PublicUserOut]:
    friends = await friend_service.list_friends(db, user)
    return [PublicUserOut.model_validate(f) for f in friends]


@router.get("/requests", response_model=list[FriendRequestOut])
async def list_requests(user: CurrentUser, db: DbSession) -> list[FriendRequestOut]:
    edges = await friend_service.list_incoming_requests(db, user)
    out: list[FriendRequestOut] = []
    for e in edges:
        requester = await db.get(User, e.requester_id)
        out.append(
            FriendRequestOut(
                id=e.id, status=e.status.value, requester=PublicUserOut.model_validate(requester)
            )
        )
    return out


@router.post("/requests/{friendship_id}/respond", response_model=FriendRequestOut)
async def respond(
    friendship_id: int, body: RespondIn, user: CurrentUser, db: DbSession
) -> FriendRequestOut:
    edge = await friend_service.respond(db, user, friendship_id, body.accept)
    if body.accept:
        await notification_service.dispatch(
            db, edge.requester_id, "friend_accepted", {"name": user.display_name or "دوست شما"}
        )
    requester = await db.get(User, edge.requester_id)
    return FriendRequestOut(
        id=edge.id, status=edge.status.value, requester=PublicUserOut.model_validate(requester)
    )


@router.delete("/{other_id}", status_code=204)
async def unfriend(other_id: int, user: CurrentUser, db: DbSession) -> None:
    await friend_service.unfriend(db, user, other_id)
