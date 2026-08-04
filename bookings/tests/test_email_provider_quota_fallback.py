import pytest
from django.core.cache import cache

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_backup_provider_is_not_used_unless_enabled(monkeypatch, settings):
    cache.clear()
    settings.EMAIL_PROVIDER = "fake"
    settings.EMAIL_DAILY_HARD_LIMIT = 0
    settings.EMAIL_BACKUP_PROVIDER_ENABLED = False
    booking, _session, _ledger = _confirm_paid_booking("quota-backup-disabled")

    from bookings.models import BookingNotification
    from bookings.services import notification_delivery

    called = {"backup": 0}
    monkeypatch.setattr(notification_delivery, "get_backup_email_provider", lambda: called.__setitem__("backup", 1))

    notification_delivery.BookingNotificationDeliveryService.send_pending(limit=10)
    assert called["backup"] == 0
    assert BookingNotification.objects.get(booking=booking).status == BookingNotification.Status.QUOTA_BLOCKED
