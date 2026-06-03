import pytest

from bookings.services.legal import NO_REFUND_NOTICE
from bookings.services.notification_delivery import build_notification_email
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_receipt_email_and_status_surface_no_refund_notice(settings, tmp_path):
    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("policy-messaging")

    from bookings.models import BookingNotification
    from bookings.views import _status_payload

    notification = BookingNotification.objects.get(booking=booking, notification_type="booking_confirmed_with_receipt")
    email = build_notification_email(notification)
    status = _status_payload(booking)

    assert NO_REFUND_NOTICE in email.text
    assert NO_REFUND_NOTICE in str(status)
    assert "grace@example.com" not in email.text
    assert "+254712345678" not in email.text
