from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class SmsProvider(Protocol):
    """Send a plain-text SMS to an E.164 number. Raise on unrecoverable failure."""

    async def send(self, to: str, text: str) -> None: ...
