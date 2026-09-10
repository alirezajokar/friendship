from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base, TimestampMixin, UTCDateTime


class FriendshipStatus(StrEnum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class Friendship(Base, TimestampMixin):
    """A directed friend request that becomes symmetric once accepted.

    Uniqueness is on the ordered pair (requester, addressee); the service layer
    also guards against the reverse pair already existing.
    """

    __tablename__ = "friendships"
    __table_args__ = (UniqueConstraint("requester_id", "addressee_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requester_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    addressee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    status: Mapped[FriendshipStatus] = mapped_column(
        Enum(FriendshipStatus, name="friendship_status"),
        nullable=False,
        default=FriendshipStatus.pending,
    )
    responded_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
