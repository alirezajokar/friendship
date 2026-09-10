from __future__ import annotations

from pydantic import BaseModel

from app.schemas.user import PublicUserOut


class InviteOut(BaseModel):
    code: str
    url: str


class InvitePreviewOut(BaseModel):
    inviter: PublicUserOut


class InviteAcceptOut(BaseModel):
    status: str
    inviter: PublicUserOut
