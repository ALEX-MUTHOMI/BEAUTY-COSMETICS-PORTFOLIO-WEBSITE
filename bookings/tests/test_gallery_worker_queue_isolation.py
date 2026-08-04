from django.conf import settings

from bookings.tasks import process_gallery_image


def test_gallery_processing_task_isolated_from_payment_and_receipt_queues():
    route = settings.CELERY_TASK_ROUTES["bookings.tasks.process_gallery_image"]

    assert route["queue"] == "gallery"
    assert process_gallery_image.queue == "gallery"
    assert "billing" not in str(route).lower()
    assert "receipts" not in str(route).lower()
