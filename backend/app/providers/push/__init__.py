"""Web Push (VAPID) delivery."""

from app.providers.push.webpush import send_web_push

__all__ = ["send_web_push"]
