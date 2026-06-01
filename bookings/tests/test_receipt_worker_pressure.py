import pytest

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_receipt_worker_processes_bounded_batches_without_sync_web_pdf_generation(settings):
    settings.EMAIL_PROVIDER = "fake"
    for index in range(12):
        _confirm_paid_booking(f"worker-pressure-{index}")

    from bookings.models import BookingNotification
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    assert BookingNotification.objects.filter(status=BookingNotification.Status.PENDING).count() == 12
    first = BookingNotificationDeliveryService.send_pending(limit=5)
    second = BookingNotificationDeliveryService.send_pending(limit=5)
    third = BookingNotificationDeliveryService.send_pending(limit=5)
    assert (first.sent, second.sent, third.sent) == (5, 5, 2)
    assert BookingNotification.objects.filter(status=BookingNotification.Status.PENDING).count() == 0
