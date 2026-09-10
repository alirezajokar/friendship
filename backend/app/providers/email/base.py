from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class EmailProvider(Protocol):
    async def send(self, to: str, subject: str, body: str) -> None: ...
