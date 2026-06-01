import pytest

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_receipt_pdf_artifact_is_generated_once_and_reused_on_email_retry(monkeypatch, settings):
    settings.EMAIL_PROVIDER = "fake"
    booking, _session, _ledger = _confirm_paid_booking("artifact-reuse")

    from bookings.models import ReceiptPDFArtifact
    from bookings.services import receipt_pdf
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    calls = {"count": 0}
    original = receipt_pdf._build_pdf_bytes

    def counted_builder(lines):
        calls["count"] += 1
        return original(lines)

    monkeypatch.setattr(receipt_pdf, "_build_pdf_bytes", counted_builder)

    first = BookingNotificationDeliveryService.send_pending(limit=10)
    assert first.sent == 1
    assert calls["count"] == 1
    artifact = ReceiptPDFArtifact.objects.get(receipt=booking.receipt)
    assert artifact.status == ReceiptPDFArtifact.Status.READY
    assert artifact.sha256_hash
    assert artifact.size_bytes > 0

    booking.notifications.update(status="pending", attempts=0, sent_at=None)
    second = BookingNotificationDeliveryService.send_pending(limit=10)
    assert second.sent == 1
    assert calls["count"] == 1
    assert ReceiptPDFArtifact.objects.filter(receipt=booking.receipt).count() == 1


@pytest.mark.django_db(transaction=True)
def test_duplicate_confirmation_does_not_create_duplicate_pdf_artifacts(settings):
    settings.EMAIL_PROVIDER = "fake"
    booking, session, ledger = _confirm_paid_booking("artifact-duplicate")

    from bookings.models import ReceiptPDFArtifact
    from bookings.services.checkout_contract import BookingCheckoutContractService
    from bookings.services.notification_delivery import BookingNotificationDeliveryService

    BookingCheckoutContractService.confirm_booking_after_billing_success(
        checkout_session=session,
        billing_ledger=ledger,
    )
    assert BookingNotificationDeliveryService.send_pending(limit=10).sent == 1
    assert ReceiptPDFArtifact.objects.filter(receipt=booking.receipt).count() == 1
