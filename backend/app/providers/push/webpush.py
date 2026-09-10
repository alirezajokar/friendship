from __future__ import annotations

import json
import logging

from pywebpush import WebPushException, webpush

from app.config import settings

log = logging.getLogger("push.webpush")


class PushGone(Exception):
    """The subscription is dead (404/410) and should be deleted."""


def send_web_push(subscription: dict, payload: dict) -> None:
    """Blocking send of one Web Push message. Call from a threadpool.

    `subscription` is ``{"endpoint": ..., "keys": {"p256dh": ..., "auth": ...}}``.
    Raises :class:`PushGone` when the endpoint is permanently invalid.
    """
    if not settings.vapid_private_key:
        log.warning("VAPID keys not configured; skipping push")
        return
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(payload),
            vapid_private_key=settings.vapid_private_key,
            vapid_claims={"sub": settings.vapid_subject},
        )
    except WebPushException as exc:
        status = getattr(exc.response, "status_code", None)
        if status in (404, 410):
            raise PushGone from exc
        log.warning("web push failed (%s): %s", status, exc)
