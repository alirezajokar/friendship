"""Application settings, loaded from environment (see .env.example)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ReminderOffset:
    """One birthday-reminder window: `days_before` at wall-clock `hour:minute`."""

    def __init__(self, days_before: int, hour: int, minute: int) -> None:
        self.days_before = days_before
        self.hour = hour
        self.minute = minute

    @property
    def key(self) -> str:
        return f"d{self.days_before}"

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"ReminderOffset({self.days_before}, {self.hour:02d}:{self.minute:02d})"


def _parse_offsets(raw: str) -> list[ReminderOffset]:
    offsets: list[ReminderOffset] = []
    for chunk in (c.strip() for c in raw.split(",") if c.strip()):
        days_s, hh, mm = chunk.split(":")
        offsets.append(ReminderOffset(int(days_s), int(hh), int(mm)))
    return offsets


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "dev"
    secret_key: str = "dev-secret-change-me"
    otp_hmac_secret: str = "dev-otp-secret-change-me"
    tz_default: str = "Asia/Tehran"

    database_url: str = "postgresql+asyncpg://friendship:friendship@localhost:5432/friendship"

    access_ttl_seconds: int = 1800
    refresh_ttl_seconds: int = 2_592_000
    refresh_absolute_ttl_seconds: int = 7_776_000
    cookie_secure: bool = False
    cookie_domain: str = ""

    frontend_origin: str = "http://localhost:5173"
    public_base_url: str = "http://localhost:5173"

    otp_length: int = 6
    otp_ttl_seconds: int = 120
    otp_max_attempts: int = 5
    otp_resend_cooldown_seconds: int = 30
    otp_max_per_hour: int = 5

    sms_provider: str = "console"
    kavenegar_api_key: str = ""
    kavenegar_sender: str = ""

    email_provider: str = "console"
    email_from: str = "Friendship <no-reply@example.com>"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = True

    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_subject: str = "mailto:admin@example.com"

    reminder_offsets: str = "7:09:00,3:09:00,1:21:00,0:09:00"

    # --- derived -----------------------------------------------------------
    @property
    def is_prod(self) -> bool:
        return self.env == "prod"

    @property
    def offsets(self) -> list[ReminderOffset]:
        return _parse_offsets(self.reminder_offsets)

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.frontend_origin.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
