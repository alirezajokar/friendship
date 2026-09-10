from __future__ import annotations

from functools import lru_cache

from app.config import settings
from app.providers.sms.base import SmsProvider
from app.providers.sms.console import ConsoleSmsProvider
from app.providers.sms.kavenegar import KavenegarSmsProvider

_PROVIDERS = {
    "console": ConsoleSmsProvider,
    "kavenegar": KavenegarSmsProvider,
}


@lru_cache
def get_sms_provider() -> SmsProvider:
    try:
        cls = _PROVIDERS[settings.sms_provider]
    except KeyError:
        raise RuntimeError(f"Unknown SMS_PROVIDER: {settings.sms_provider!r}") from None
    return cls()
