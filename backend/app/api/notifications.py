from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import delete, select

from app.core.deps import CurrentUser, DbSession, enforce_csrf
from app.models import PushSubscription
from app.schemas.notification import (
    NotificationOut,
    PrefsIn,
    PrefsOut,
    PushSubscriptionIn,
)
from app.services import notification_service

router = APIRouter(tags=["notifications"], dependencies=[Depends(enforce_csrf)])


@router.get("/notifications", response_model=list[NotificationOut])
async def list_notifications(user: CurrentUser, db: DbSession) -> list[NotificationOut]:
    notes = await notification_service.list_for_user(db, user)
    return [NotificationOut.model_validate(n) for n in notes]


@router.post("/notifications/{note_id}/read", status_code=204)
async def read_notification(note_id: int, user: CurrentUser, db: DbSession) -> None:
    await notification_service.mark_read(db, user, note_id)


@router.get("/notifications/prefs", response_model=PrefsOut)
async def get_prefs(user: CurrentUser, db: DbSession) -> PrefsOut:
    pref = await notification_service.get_or_create_prefs(db, user)
    return PrefsOut.model_validate(pref)


@router.put("/notifications/prefs", response_model=PrefsOut)
async def set_prefs(body: PrefsIn, user: CurrentUser, db: DbSession) -> PrefsOut:
    pref = await notification_service.get_or_create_prefs(db, user)
    pref.web_push = body.web_push
    pref.email = body.email
    await db.commit()
    await db.refresh(pref)
    return PrefsOut.model_validate(pref)


@router.post("/push/subscribe", status_code=204)
async def push_subscribe(body: PushSubscriptionIn, user: CurrentUser, db: DbSession) -> None:
    existing = (
        await db.execute(
            select(PushSubscription).where(PushSubscription.endpoint == body.endpoint)
        )
    ).scalar_one_or_none()
    if existing is not None:
        existing.user_id = user.id
        existing.p256dh = body.keys.get("p256dh", "")
        existing.auth = body.keys.get("auth", "")
    else:
        db.add(
            PushSubscription(
                user_id=user.id,
                endpoint=body.endpoint,
                p256dh=body.keys.get("p256dh", ""),
                auth=body.keys.get("auth", ""),
            )
        )
    await db.commit()


@router.post("/push/unsubscribe", status_code=204)
async def push_unsubscribe(body: PushSubscriptionIn, user: CurrentUser, db: DbSession) -> None:
    await db.execute(
        delete(PushSubscription).where(
            PushSubscription.endpoint == body.endpoint,
            PushSubscription.user_id == user.id,
        )
    )
    await db.commit()
