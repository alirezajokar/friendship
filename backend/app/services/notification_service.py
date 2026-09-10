"""Fan-out for a single notification: in-app row + Web Push + email."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, NotificationPref, PushSubscription, User
from app.providers.email import get_email_provider
from app.providers.push.webpush import PushGone, send_web_push

log = logging.getLogger("notifications")

# type -> (title, body-template). payload keys are substituted into the body.
_TEMPLATES = {
    "friend_request": ("درخواست دوستی جدید", "{name} می‌خواهد با شما دوست شود."),
    "friend_accepted": ("دوستی تأیید شد", "{name} درخواست دوستی شما را پذیرفت."),
    "birthday": ("یادآوری تولد", "{days_text} تا تولد {name}."),
}


def _render(ntype: str, payload: dict) -> tuple[str, str]:
    title, body_tpl = _TEMPLATES.get(ntype, (ntype, ""))
    try:
        return title, body_tpl.format(**payload)
    except (KeyError, IndexError):
        return title, body_tpl


async def get_or_create_prefs(db: AsyncSession, user: User) -> NotificationPref:
    pref = await db.get(NotificationPref, user.id)
    if pref is None:
        pref = NotificationPref(user_id=user.id)
        db.add(pref)
        await db.commit()
        await db.refresh(pref)
    return pref


async def dispatch(db: AsyncSession, recipient_id: int, ntype: str, payload: dict) -> Notification:
    note = Notification(recipient_id=recipient_id, type=ntype, payload=payload)
    db.add(note)
    await db.commit()
    await db.refresh(note)

    recipient = await db.get(User, recipient_id)
    pref = await get_or_create_prefs(db, recipient)
    title, body = _render(ntype, payload)

    if pref.web_push:
        await _push_all(db, recipient_id, {"title": title, "body": body, "type": ntype})
    if pref.email and recipient.email:
        try:
            await get_email_provider().send(recipient.email, title, body)
        except Exception:  # noqa: BLE001
            log.exception("email notify failed for user %s", recipient_id)

    return note


async def _push_all(db: AsyncSession, user_id: int, message: dict) -> None:
    subs = list(
        (
            await db.execute(
                select(PushSubscription).where(PushSubscription.user_id == user_id)
            )
        )
        .scalars()
        .all()
    )
    for sub in subs:
        info = {"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}}
        try:
            await asyncio.to_thread(send_web_push, info, message)
        except PushGone:
            await db.delete(sub)
        except Exception:  # noqa: BLE001
            log.exception("web push failed for sub %s", sub.id)
    await db.commit()


async def list_for_user(db: AsyncSession, user: User, limit: int = 50) -> list[Notification]:
    return list(
        (
            await db.execute(
                select(Notification)
                .where(Notification.recipient_id == user.id)
                .order_by(Notification.id.desc())
                .limit(limit)
            )
        )
        .scalars()
        .all()
    )


async def mark_read(db: AsyncSession, user: User, notification_id: int) -> None:
    note = await db.get(Notification, notification_id)
    if note is None or note.recipient_id != user.id:
        return
    if note.read_at is None:
        from datetime import UTC, datetime

        note.read_at = datetime.now(UTC)
        await db.commit()
