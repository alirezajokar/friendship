from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, TimestampMixin


class ReminderLog(Base, TimestampMixin):
    """Idempotency ledger for birthday reminders.

    Keyed by the *Jalali year of the occurrence* (not the Gregorian year) so
    windows that straddle Nowruz / the Dec–Jan boundary never double-fire.
    """

    __tablename__ = "reminder_logs"
    __table_args__ = (
        UniqueConstraint(
            "recipient_id", "birthday_user_id", "occurrence_jyear", "offset_key"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    birthday_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    occurrence_jyear: Mapped[int] = mapped_column(Integer, nullable=False)
    offset_key: Mapped[str] = mapped_column(String(8), nullable=False)
