from __future__ import annotations

from pydantic import BaseModel, Field


class OtpRequestIn(BaseModel):
    phone: str = Field(min_length=3, max_length=20)


class OtpRequestOut(BaseModel):
    resend_cooldown_seconds: int


class OtpVerifyIn(BaseModel):
    phone: str = Field(min_length=3, max_length=20)
    code: str = Field(min_length=4, max_length=8)


class SessionOut(BaseModel):
    is_new: bool
    profile_completed: bool
