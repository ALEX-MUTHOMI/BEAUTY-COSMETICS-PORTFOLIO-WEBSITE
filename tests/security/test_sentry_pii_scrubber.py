from core.sentry_scrubber import scrub_pii_text, scrub_sentry_event


def test_scrub_pii_text_redacts_email_and_kenyan_msisdn():
    text = scrub_pii_text("Customer grace@example.com phone +254712345678")
    assert "grace@example.com" not in text
    assert "+254712345678" not in text
    assert "[REDACTED]" in text


def test_scrub_sentry_event_redacts_nested_secrets():
    event = scrub_sentry_event(
        {
            "message": "hold failed for grace@example.com",
            "extra": {"phone": "+254712345678", "booking_id": "11111111-1111-4111-8111-111111111111"},
            "request": {"headers": {"Authorization": "Bearer secret-token"}},
        }
    )
    serialized = str(event)
    assert "grace@example.com" not in serialized
    assert "+254712345678" not in serialized
    assert "secret-token" not in serialized
    assert event["extra"]["phone"] == "[REDACTED]"
