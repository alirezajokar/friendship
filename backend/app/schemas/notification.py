from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    payload: dict
    created_at: datetime
    read_at: datetime | None


class PrefsIn(BaseModel):
    web_push: bool
    email: bool


class PrefsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    web_push: bool
    email: bool


class PushSubscriptionIn(BaseModel):
    endpoint: str
    keys: dict  # {"p256dh": ..., "auth": ...}
