import pytest

from bookings.models import Booking, BookingNotification
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_provider_timeout_does_not_deconfirm_or_duplicate_notification(monkeypatch, settings):
    settings.EMAIL_PROVIDER = "fake"
    booking, _session, _ledger = _confirm_paid_booking("provider-timeout")

    from bookings.services import notification_delivery
    from bookings.services.email_provider import EmailProviderError

    class TimeoutProvider:
        def send_email(self, **kwargs):
            raise EmailProviderError("timeout from provider api key hidden")

    monkeypatch.setattr(notification_delivery, "get_email_provider", lambda: TimeoutProvider())

    result = notification_delivery.BookingNotificationDeliveryService.send_pending(limit=10)
    booking.refresh_from_db()
    assert result.sent == 0
    assert result.failed == 1
    assert booking.status == Booking.Status.CONFIRMED
    assert BookingNotification.objects.filter(booking=booking).count() == 1
    assert BookingNotification.objects.get(booking=booking).last_error_redacted
