import pytest


@pytest.mark.django_db
def test_fake_email_provider_normalizes_success_and_redacts_recipient(settings):
    settings.EMAIL_PROVIDER = "fake"

    from bookings.services.email_provider import get_email_provider

    provider = get_email_provider()
    result = provider.send_email(
        to_hash="hash",
        to_redacted="g***@example.com",
        subject="Booking confirmed",
        html="<p>safe</p>",
        text="safe",
        attachments=[],
        metadata={"booking_reference": "public-ref"},
    )
    assert result.accepted is True
    assert result.provider_message_id
    assert "grace@example.com" not in str(result)


@pytest.mark.django_db
def test_resend_provider_requires_api_key_and_redacts_errors(settings, caplog):
    settings.EMAIL_PROVIDER = "resend"
    settings.EMAIL_PROVIDER_API_KEY = ""

    from bookings.services.email_provider import EmailProviderError, get_email_provider

    provider = get_email_provider()
    with pytest.raises(EmailProviderError) as exc:
        provider.send_email(
            to_hash="hash",
            to_redacted="g***@example.com",
            subject="Booking confirmed\r\nBcc: attacker@example.com",
            html="<p>safe</p>",
            text="safe",
            attachments=[],
            metadata={},
        )
    surface = f"{exc.value} {caplog.text}"
    assert "api" in surface.lower()
    assert "attacker@example.com" not in surface
    assert "\r" not in surface and "\nBcc" not in surface


@pytest.mark.django_db
def test_real_email_provider_rejects_non_https_provider_url(settings):
    settings.EMAIL_PROVIDER = "resend"
    settings.EMAIL_PROVIDER_API_KEY = "provider-placeholder-value"  # pragma: allowlist secret
    settings.EMAIL_PROVIDER_BASE_URL = "http://api.resend.example/emails"

    from bookings.services.email_provider import EmailProviderError, get_email_provider

    provider = get_email_provider()
    with pytest.raises(EmailProviderError) as exc:
        provider.send_email(
            to_hash="hash",
            to_redacted="g***@example.com",
            subject="Payment receipt",
            html="<p>safe</p>",
            text="safe",
            attachments=[],
            metadata={},
        )
    assert "HTTPS" in str(exc.value)
    assert "provider-placeholder-value" not in str(exc.value)
