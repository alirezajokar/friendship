from __future__ import annotations

import logging

log = logging.getLogger("sms.console")


class ConsoleSmsProvider:
    """Dev provider: logs the message instead of sending. Read OTP codes here."""

    async def send(self, to: str, text: str) -> None:
        log.warning("SMS -> %s | %s", to, text)
