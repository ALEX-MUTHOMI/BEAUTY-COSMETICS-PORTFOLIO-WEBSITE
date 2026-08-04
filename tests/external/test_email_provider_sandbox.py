import os

import pytest

pytestmark = [pytest.mark.external, pytest.mark.payment_contract]


def _email_env_ready():
    return (
        os.getenv("RUN_EXTERNAL_EMAIL_TESTS", "").lower() == "true"
        and bool(os.getenv("EMAIL_EXTERNAL_TEST_RECIPIENT"))
        and bool(os.getenv("EMAIL_PROVIDER_API_KEY"))
        and os.getenv("EMAIL_PROVIDER", "") in {"resend", "mailgun"}
    )


@pytest.mark.django_db
def test_external_email_provider_sandbox_opt_in(settings):
    if not _email_env_ready():
        pytest.skip("external email provider test requires explicit opt-in env")
    settings.EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER")
    settings.EMAIL_PROVIDER_API_KEY = os.getenv("EMAIL_PROVIDER_API_KEY")
    settings.EMAIL_EXTERNAL_TEST_RECIPIENT = os.getenv("EMAIL_EXTERNAL_TEST_RECIPIENT")

    from bookings.services.email_provider import get_email_provider

    provider = get_email_provider()
    result = provider.send_email(
        to_hash="external-test-recipient",
        to_redacted="e***@example.test",
        subject="AestheticOS receipt delivery test",
        html="<p>Provider contract test.</p>",
        text="Provider contract test.",
        attachments=[],
        metadata={"test": "external_email_provider_sandbox"},
    )
    assert result.accepted is True
