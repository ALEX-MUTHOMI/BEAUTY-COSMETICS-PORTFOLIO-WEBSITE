import pytest
from django.db import transaction

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_receipt_notification_task_dispatches_only_after_commit(monkeypatch):
    dispatched = []

    from bookings.services import receipts

    monkeypatch.setattr(
        receipts, "enqueue_receipt_notification_task", lambda notification_id: dispatched.append(notification_id)
    )

    with transaction.atomic():
        booking, _session, _ledger = _confirm_paid_booking("on-commit-safe")
        assert dispatched == []

    assert len(dispatched) == 1
    assert str(booking.notifications.get().id) == str(dispatched[0])


@pytest.mark.django_db(transaction=True)
def test_rollback_does_not_dispatch_receipt_notification_task(monkeypatch):
    dispatched = []

    from bookings.services import receipts

    monkeypatch.setattr(
        receipts, "enqueue_receipt_notification_task", lambda notification_id: dispatched.append(notification_id)
    )

    with pytest.raises(RuntimeError):
        with transaction.atomic():
            _confirm_paid_booking("on-commit-rollback")
            raise RuntimeError("force rollback")

    assert dispatched == []


@pytest.mark.django_db(transaction=True)
def test_on_commit_dispatch_failure_leaves_outbox_sweepable(monkeypatch, settings):
    settings.EMAIL_PROVIDER = "fake"

    from bookings.services import receipts

    monkeypatch.setattr(
        receipts,
        "enqueue_receipt_notification_task",
        lambda notification_id: (_ for _ in ()).throw(RuntimeError("broker unavailable")),
    )

    booking, _session, _ledger = _confirm_paid_booking("on-commit-broker-down")

    from bookings.models import BookingNotification
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    assert BookingNotification.objects.filter(booking=booking, status=BookingNotification.Status.PENDING).count() == 1
    assert BookingNotificationDeliveryService.send_pending(limit=10).sent == 1
