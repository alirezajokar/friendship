from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DbSession, enforce_csrf
from app.schemas.wishlist import (
    FriendItemOut,
    OwnItemOut,
    WishlistItemIn,
    WishlistItemPatch,
)
from app.services import wishlist_service

router = APIRouter(prefix="/wishlists", tags=["wishlists"], dependencies=[Depends(enforce_csrf)])


@router.get("/me", response_model=list[OwnItemOut])
async def my_items(user: CurrentUser, db: DbSession) -> list[OwnItemOut]:
    items = await wishlist_service.list_own(db, user)
    return [OwnItemOut.model_validate(i) for i in items]


@router.post("/items", response_model=OwnItemOut, status_code=201)
async def create_item(body: WishlistItemIn, user: CurrentUser, db: DbSession) -> OwnItemOut:
    item = await wishlist_service.create_item(db, user, **body.model_dump())
    return OwnItemOut.model_validate(item)


@router.patch("/items/{item_id}", response_model=OwnItemOut)
async def patch_item(
    item_id: int, body: WishlistItemPatch, user: CurrentUser, db: DbSession
) -> OwnItemOut:
    fields = body.model_dump(exclude_unset=True)
    item = await wishlist_service.update_item(db, user, item_id, **fields)
    return OwnItemOut.model_validate(item)


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int, user: CurrentUser, db: DbSession) -> None:
    await wishlist_service.delete_item(db, user, item_id)


@router.get("/{owner_id}", response_model=list[FriendItemOut])
async def friend_items(owner_id: int, user: CurrentUser, db: DbSession) -> list[FriendItemOut]:
    views = await wishlist_service.list_for_friend(db, user, owner_id)
    return [
        FriendItemOut(
            id=v.item.id,
            title=v.item.title,
            description=v.item.description,
            url=v.item.url,
            image_url=v.item.image_url,
            price=v.item.price,
            position=v.item.position,
            is_claimed=v.is_claimed,
            claimed_by_me=v.claimed_by_me,
        )
        for v in views
    ]


@router.post("/items/{item_id}/claim", status_code=204)
async def claim(item_id: int, user: CurrentUser, db: DbSession) -> None:
    await wishlist_service.claim_item(db, user, item_id)


@router.delete("/items/{item_id}/claim", status_code=204)
async def unclaim(item_id: int, user: CurrentUser, db: DbSession) -> None:
    await wishlist_service.unclaim_item(db, user, item_id)
