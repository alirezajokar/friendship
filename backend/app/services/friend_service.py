"""Friend requests and the symmetric friendship they become once accepted."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models import Friendship, FriendshipStatus, User


def _pair(a: int, b: int):
    return or_(
        and_(Friendship.requester_id == a, Friendship.addressee_id == b),
        and_(Friendship.requester_id == b, Friendship.addressee_id == a),
    )


async def _edge(db: AsyncSession, a: int, b: int) -> Friendship | None:
    return (await db.execute(select(Friendship).where(_pair(a, b)))).scalars().first()


async def are_friends(db: AsyncSession, a: int, b: int) -> bool:
    edge = await _edge(db, a, b)
    return edge is not None and edge.status == FriendshipStatus.accepted


async def send_request(db: AsyncSession, requester: User, addressee_id: int) -> Friendship:
    if addressee_id == requester.id:
        raise AppError(422, "cannot_friend_self")
    if await db.get(User, addressee_id) is None:
        raise AppError(404, "user_not_found")

    edge = await _edge(db, requester.id, addressee_id)
    if edge is not None:
        if edge.status == FriendshipStatus.accepted:
            return edge
        if edge.status == FriendshipStatus.pending:
            # Reverse pending request -> accept it instead of stacking another.
            if edge.addressee_id == requester.id:
                edge.status = FriendshipStatus.accepted
                edge.responded_at = datetime.now(UTC)
                await db.commit()
            return edge
        # previously declined -> allow a fresh request
        edge.requester_id = requester.id
        edge.addressee_id = addressee_id
        edge.status = FriendshipStatus.pending
        edge.responded_at = None
        await db.commit()
        return edge

    edge = Friendship(
        requester_id=requester.id,
        addressee_id=addressee_id,
        status=FriendshipStatus.pending,
    )
    db.add(edge)
    await db.commit()
    await db.refresh(edge)
    return edge


async def respond(db: AsyncSession, user: User, friendship_id: int, accept: bool) -> Friendship:
    edge = await db.get(Friendship, friendship_id)
    if edge is None or edge.addressee_id != user.id:
        raise AppError(404, "request_not_found")
    if edge.status != FriendshipStatus.pending:
        raise AppError(409, "request_not_pending")
    edge.status = FriendshipStatus.accepted if accept else FriendshipStatus.declined
    edge.responded_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(edge)
    return edge


async def list_friends(db: AsyncSession, user: User) -> list[User]:
    rows = (
        await db.execute(
            select(Friendship).where(
                Friendship.status == FriendshipStatus.accepted,
                or_(Friendship.requester_id == user.id, Friendship.addressee_id == user.id),
            )
        )
    ).scalars().all()
    other_ids = [
        r.addressee_id if r.requester_id == user.id else r.requester_id for r in rows
    ]
    if not other_ids:
        return []
    return list(
        (await db.execute(select(User).where(User.id.in_(other_ids)))).scalars().all()
    )


async def list_incoming_requests(db: AsyncSession, user: User) -> list[Friendship]:
    return list(
        (
            await db.execute(
                select(Friendship).where(
                    Friendship.addressee_id == user.id,
                    Friendship.status == FriendshipStatus.pending,
                )
            )
        )
        .scalars()
        .all()
    )


async def unfriend(db: AsyncSession, user: User, other_id: int) -> None:
    edge = await _edge(db, user.id, other_id)
    if edge is None or edge.status != FriendshipStatus.accepted:
        raise AppError(404, "not_friends")
    await db.delete(edge)
    await db.commit()
