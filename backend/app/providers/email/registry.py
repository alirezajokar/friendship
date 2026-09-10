from __future__ import annotations

from functools import lru_cache

from app.config import settings
from app.providers.email.base import EmailProvider
from app.providers.email.console import ConsoleEmailProvider
from app.providers.email.smtp import SmtpEmailProvider

_PROVIDERS = {
    "console": ConsoleEmailProvider,
    "smtp": SmtpEmailProvider,
}


@lru_cache
def get_email_provider() -> EmailProvider:
    try:
        cls = _PROVIDERS[settings.email_provider]
    except KeyError:
        raise RuntimeError(f"Unknown EMAIL_PROVIDER: {settings.email_provider!r}") from None
    return cls()
