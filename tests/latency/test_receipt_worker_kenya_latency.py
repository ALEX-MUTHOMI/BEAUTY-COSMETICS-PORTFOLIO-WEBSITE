import time

import pytest

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_slow_pdf_for_one_receipt_does_not_block_following_notifications(monkeypatch, settings):
    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_TIMEOUT_SECONDS = 0.01
    slow, _session, _ledger = _confirm_paid_booking("latency-slow-pdf")
    fast, _session, _ledger = _confirm_paid_booking("latency-fast-pdf")

    from bookings.models import BookingNotification
    from bookings.services import receipt_pdf
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    original = receipt_pdf._build_pdf_bytes

    def maybe_slow(lines):
        if any(slow.receipt.receipt_number in str(line) for line in lines):
            time.sleep(0.05)
        return original(lines)

    monkeypatch.setattr(receipt_pdf, "_build_pdf_bytes", maybe_slow)

    result = BookingNotificationDeliveryService.send_pending(limit=10)
    assert result.sent == 1
    assert result.failed == 1
    assert BookingNotification.objects.get(booking=fast).status == BookingNotification.Status.SENT
