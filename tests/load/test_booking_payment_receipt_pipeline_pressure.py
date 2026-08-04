import pytest

from bookings.models import Booking, BookingNotification, BookingReceipt
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
@pytest.mark.payment_load
def test_one_hundred_payment_receipt_pipelines_do_not_wait_on_email_provider(settings, tmp_path):
    settings.EMAIL_PROVIDER = "fake"
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)

    for index in range(100):
        _confirm_paid_booking(f"b4d-pressure-{index}")

    assert Booking.objects.filter(status=Booking.Status.CONFIRMED).count() == 100
    assert BookingReceipt.objects.count() == 100
    assert BookingNotification.objects.filter(status=BookingNotification.Status.PENDING).count() == 100
    assert BookingNotification.objects.values("booking_id", "notification_type").distinct().count() == 100
