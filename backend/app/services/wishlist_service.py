"""Wishlist items and gift claims.

Visibility rules (enforced here, never in the router):

* The **owner** sees their items with *no* claim information — the surprise is
  preserved.
* A **friend** sees every item plus two booleans: ``is_claimed`` (someone took
  it) and ``claimed_by_me``. The identity of another friend's claim is never
  exposed.
* Only a friend (not the owner) may claim; only the claimer may release it.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models import User, WishlistClaim, WishlistItem
from app.services import friend_service


@dataclass
class FriendView:
    item: WishlistItem
    is_claimed: bool
    claimed_by_me: bool


async def list_own(db: AsyncSession, user: User) -> list[WishlistItem]:
    return list(
        (
            await db.execute(
                select(WishlistItem)
                .where(WishlistItem.owner_id == user.id)
                .order_by(WishlistItem.position, WishlistItem.id)
            )
        )
        .scalars()
        .all()
    )


async def create_item(db: AsyncSession, user: User, **fields) -> WishlistItem:
    item = WishlistItem(owner_id=user.id, **fields)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def _own_item(db: AsyncSession, user: User, item_id: int) -> WishlistItem:
    item = await db.get(WishlistItem, item_id)
    if item is None or item.owner_id != user.id:
        raise AppError(404, "item_not_found")
    return item


async def update_item(db: AsyncSession, user: User, item_id: int, **fields) -> WishlistItem:
    item = await _own_item(db, user, item_id)
    for key, value in fields.items():
        if value is not None:
            setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, user: User, item_id: int) -> None:
    item = await _own_item(db, user, item_id)
    await db.delete(item)  # claim rows cascade
    await db.commit()


async def list_for_friend(db: AsyncSession, viewer: User, owner_id: int) -> list[FriendView]:
    if owner_id == viewer.id:
        raise AppError(422, "use_own_endpoint")
    if not await friend_service.are_friends(db, viewer.id, owner_id):
        raise AppError(403, "not_friends")

    items = list(
        (
            await db.execute(
                select(WishlistItem)
                .where(WishlistItem.owner_id == owner_id)
                .order_by(WishlistItem.position, WishlistItem.id)
            )
        )
        .scalars()
        .all()
    )
    if not items:
        return []
    claims = {
        c.item_id: c.claimed_by_id
        for c in (
            await db.execute(
                select(WishlistClaim).where(
                    WishlistClaim.item_id.in_([i.id for i in items])
                )
            )
        )
        .scalars()
        .all()
    }
    return [
        FriendView(
            item=i,
            is_claimed=i.id in claims,
            claimed_by_me=claims.get(i.id) == viewer.id,
        )
        for i in items
    ]


async def claim_item(db: AsyncSession, viewer: User, item_id: int) -> None:
    item = await db.get(WishlistItem, item_id)
    if item is None:
        raise AppError(404, "item_not_found")
    if item.owner_id == viewer.id:
        raise AppError(403, "cannot_claim_own")
    if not await friend_service.are_friends(db, viewer.id, item.owner_id):
        raise AppError(403, "not_friends")

    db.add(WishlistClaim(item_id=item_id, claimed_by_id=viewer.id))
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AppError(409, "already_claimed") from None


async def unclaim_item(db: AsyncSession, viewer: User, item_id: int) -> None:
    claim = (
        await db.execute(select(WishlistClaim).where(WishlistClaim.item_id == item_id))
    ).scalar_one_or_none()
    if claim is None:
        raise AppError(404, "not_claimed")
    if claim.claimed_by_id != viewer.id:
        raise AppError(403, "not_your_claim")
    await db.delete(claim)
    await db.commit()
