from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class WishlistItemIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    url: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=1000)
    price: Decimal | None = Field(default=None, ge=0)
    position: int = 0


class WishlistItemPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    url: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=1000)
    price: Decimal | None = Field(default=None, ge=0)
    position: int | None = None


class OwnItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    url: str | None
    image_url: str | None
    price: Decimal | None
    position: int


class FriendItemOut(BaseModel):
    id: int
    title: str
    description: str | None
    url: str | None
    image_url: str | None
    price: Decimal | None
    position: int
    is_claimed: bool
    claimed_by_me: bool
