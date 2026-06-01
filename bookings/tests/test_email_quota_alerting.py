import pytest
from django.core.cache import cache

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_email_soft_limit_emits_alert_and_continues_sending(settings, caplog):
    cache.clear()
    settings.EMAIL_PROVIDER = "fake"
    settings.EMAIL_DAILY_SOFT_LIMIT = 1
    settings.EMAIL_DAILY_HARD_LIMIT = 10
    _confirm_paid_booking("quota-soft-one")
    _confirm_paid_booking("quota-soft-two")

    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    result = BookingNotificationDeliveryService.send_pending(limit=10)
    assert result.sent == 2
    assert "email.quota.soft_limit_reached" in caplog.text


@pytest.mark.django_db(transaction=True)
def test_email_hard_limit_blocks_send_but_keeps_booking_confirmed(settings, caplog):
    cache.clear()
    settings.EMAIL_PROVIDER = "fake"
    settings.EMAIL_DAILY_HARD_LIMIT = 0
    booking, _session, _ledger = _confirm_paid_booking("quota-hard")

    from bookings.models import Booking, BookingNotification
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    result = BookingNotificationDeliveryService.send_pending(limit=10)
    booking.refresh_from_db()
    notification = BookingNotification.objects.get(booking=booking)
    assert result.sent == 0
    assert booking.status == Booking.Status.CONFIRMED
    assert notification.status == BookingNotification.Status.QUOTA_BLOCKED
    assert "email.quota.hard_limit_reached" in caplog.text
