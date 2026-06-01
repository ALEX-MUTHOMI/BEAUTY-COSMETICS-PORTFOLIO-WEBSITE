import os

import pytest


@pytest.mark.external
def test_resend_provider_external_delivery_is_opt_in(settings):
    if os.getenv("RUN_EXTERNAL_EMAIL_TESTS", "false").lower() not in {"1", "true", "t"}:
        pytest.skip("External email delivery is opt-in only.")
    if not os.getenv("EMAIL_PROVIDER_API_KEY") or not os.getenv("EMAIL_EXTERNAL_TEST_RECIPIENT"):
        pytest.skip("External email provider credentials/recipient are not configured.")

    settings.EMAIL_PROVIDER = "resend"
    settings.EMAIL_PROVIDER_API_KEY = os.environ["EMAIL_PROVIDER_API_KEY"]
    settings.EMAIL_EXTERNAL_TEST_RECIPIENT = os.environ["EMAIL_EXTERNAL_TEST_RECIPIENT"]

    from bookings.services.email_provider import get_email_provider

    result = get_email_provider().send_email(
        to_hash="external-test-recipient-hash",
        to_redacted="external-recipient-redacted",
        subject="Beauty SaaS receipt delivery sandbox test",
        html="<p>Sandbox delivery test.</p>",
        text="Sandbox delivery test.",
        attachments=[],
        metadata={"purpose": "external_email_provider_contract"},
    )
    assert result.accepted is True
    assert result.provider == "resend"
