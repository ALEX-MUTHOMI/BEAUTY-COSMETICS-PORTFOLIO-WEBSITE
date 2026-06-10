# Compatibility wrapper. Canonical implementation lives in bookings.infrastructure.email_provider.
# New code should import from bookings.infrastructure.email_provider.
from bookings.infrastructure.email_provider import *  # noqa: F401,F403
from bookings.infrastructure.email_provider import (  # noqa: F811
    FAKE_EMAIL_OUTBOX,
    ConsoleEmailProvider,
    EmailProviderError,
    EmailSendResult,
    FakeEmailProvider,
    MailgunEmailProvider,
    ResendEmailProvider,
    get_email_provider,
    redact_email_error,
    reset_fake_email_outbox,
)

__all__ = [
    "FAKE_EMAIL_OUTBOX",
    "ConsoleEmailProvider",
    "EmailProviderError",
    "EmailSendResult",
    "FakeEmailProvider",
    "MailgunEmailProvider",
    "ResendEmailProvider",
    "get_email_provider",
    "redact_email_error",
    "reset_fake_email_outbox",
]
