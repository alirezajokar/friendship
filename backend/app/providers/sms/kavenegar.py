from __future__ import annotations

import httpx

from app.config import settings


class KavenegarSmsProvider:
    """Skeleton for Kavenegar (https://kavenegar.com/rest.html).

    Fill in and set SMS_PROVIDER=kavenegar plus KAVENEGAR_API_KEY / KAVENEGAR_SENDER.
    """

    BASE = "https://api.kavenegar.com/v1"

    def __init__(self) -> None:
        self.api_key = settings.kavenegar_api_key
        self.sender = settings.kavenegar_sender

    async def send(self, to: str, text: str) -> None:
        if not self.api_key:
            raise NotImplementedError("KAVENEGAR_API_KEY is not configured")
        # TODO: verify endpoint/params against current Kavenegar docs before production use.
        url = f"{self.BASE}/{self.api_key}/sms/send.json"
        params = {"receptor": to, "message": text}
        if self.sender:
            params["sender"] = self.sender
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, params=params)
            resp.raise_for_status()
