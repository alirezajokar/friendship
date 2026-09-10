"""Import all models so Alembic autogenerate and mappers see them."""

from app.models.friendship import Friendship, FriendshipStatus
from app.models.invite import Invite
from app.models.notification import Notification, NotificationPref, PushSubscription
from app.models.otp import OtpCode
from app.models.reminder import ReminderLog
from app.models.session import SessionToken
from app.models.user import User
from app.models.wishlist import WishlistClaim, WishlistItem

__all__ = [
    "Friendship",
    "FriendshipStatus",
    "Invite",
    "Notification",
    "NotificationPref",
    "PushSubscription",
    "OtpCode",
    "ReminderLog",
    "SessionToken",
    "User",
    "WishlistClaim",
    "WishlistItem",
]
