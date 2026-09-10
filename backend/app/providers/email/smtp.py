from __future__ import annotations

from email.message import EmailMessage

import aiosmtplib

from app.config import settings


class SmtpEmailProvider:
    async def send(self, to: str, subject: str, body: str) -> None:
        if not settings.smtp_host:
            raise NotImplementedError("SMTP_HOST is not configured")
        msg = EmailMessage()
        msg["From"] = settings.email_from
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            start_tls=settings.smtp_starttls,
        )
