from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Birthday — Jalali components are the source of truth. year is optional.
    birth_jyear: Mapped[int | None] = mapped_column(Integer, nullable=True)
    birth_jmonth: Mapped[int | None] = mapped_column(Integer, nullable=True)
    birth_jday: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Derived Gregorian date, for display / age only. Never used for reminder math.
    birth_gregorian: Mapped[date | None] = mapped_column(Date, nullable=True)

    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Tehran")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    @property
    def profile_completed(self) -> bool:
        return bool(self.display_name)

    @property
    def has_birthday(self) -> bool:
        return self.birth_jmonth is not None and self.birth_jday is not None
