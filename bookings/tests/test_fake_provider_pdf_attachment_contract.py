import pytest

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_fake_provider_records_one_redacted_pdf_attachment(settings, tmp_path):
    from bookings.services.email_provider import FAKE_EMAIL_OUTBOX, reset_fake_email_outbox
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_STORAGE_DIR = str(tmp_path)
    reset_fake_email_outbox()
    _confirm_paid_booking("fake-provider-attachment")

    result = BookingNotificationDeliveryService.send_pending(limit=10)

    assert result.sent == 1
    assert len(FAKE_EMAIL_OUTBOX) == 1
    message = FAKE_EMAIL_OUTBOX[0]
    assert message["provider"] == "fake"
    assert "grace@example.com" not in str(message)
    assert "+254712345678" not in str(message)
    assert len(message["attachments"]) == 1
    attachment = message["attachments"][0]
    assert attachment["filename"].endswith(".pdf")
    assert attachment["content_type"] == "application/pdf"
    assert attachment["size_bytes"] > 0
    assert attachment["sha256"]
