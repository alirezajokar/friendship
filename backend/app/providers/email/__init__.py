"""Email delivery. Pick a provider with the EMAIL_PROVIDER env var."""

from app.providers.email.registry import get_email_provider

__all__ = ["get_email_provider"]
