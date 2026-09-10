from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BirthdayIn(BaseModel):
    """Jalali components. Year optional; month/day required together."""

    jyear: int | None = Field(default=None, ge=1200, le=1500)
    jmonth: int = Field(ge=1, le=12)
    jday: int = Field(ge=1, le=31)


class ProfileUpdateIn(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=80)
    email: str | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(default=None, max_length=500)
    timezone: str | None = Field(default=None, max_length=64)
    birthday: BirthdayIn | None = None

    @model_validator(mode="after")
    def _email_shape(self):
        if self.email is not None and self.email != "" and "@" not in self.email:
            raise ValueError("email_invalid")
        return self


class PublicUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str | None
    avatar_url: str | None


class MeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone: str
    display_name: str | None
    email: str | None
    avatar_url: str | None
    timezone: str
    profile_completed: bool
    birth_jyear: int | None
    birth_jmonth: int | None
    birth_jday: int | None
    birth_gregorian: date | None
