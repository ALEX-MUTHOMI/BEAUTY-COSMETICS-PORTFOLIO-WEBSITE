import pytest
from django.conf import settings


@pytest.mark.django_db
def test_receipt_tasks_use_dedicated_queue_and_payment_callbacks_stay_on_billing_queue():
    routes = settings.CELERY_TASK_ROUTES
    assert routes["bookings.tasks.process_booking_notification"]["queue"] == "receipts"
    assert routes["bookings.tasks.sweep_booking_notifications"]["queue"] == "receipts"
    assert routes["billing.tasks.process_mpesa_webhook"]["queue"] == "billing"
    assert (
        routes["billing.tasks.process_mpesa_webhook"]["queue"]
        != routes["bookings.tasks.process_booking_notification"]["queue"]
    )
