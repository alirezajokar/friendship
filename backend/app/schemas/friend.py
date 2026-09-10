from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.schemas.user import PublicUserOut


class FriendRequestOut(BaseModel):
    id: int
    status: str
    requester: PublicUserOut


class RespondIn(BaseModel):
    accept: bool


class FriendListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    friends: list[PublicUserOut]
