"""SMS delivery. Pick a provider with the SMS_PROVIDER env var."""

from app.providers.sms.registry import get_sms_provider

__all__ = ["get_sms_provider"]
