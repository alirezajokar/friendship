from __future__ import annotations

import logging

log = logging.getLogger("email.console")


class ConsoleEmailProvider:
    async def send(self, to: str, subject: str, body: str) -> None:
        log.warning("EMAIL -> %s | %s\n%s", to, subject, body)
