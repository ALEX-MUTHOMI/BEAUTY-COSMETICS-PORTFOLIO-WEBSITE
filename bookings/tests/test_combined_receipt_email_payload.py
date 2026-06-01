import pytest

from bookings.models import BookingNotification
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking


@pytest.mark.django_db(transaction=True)
def test_one_combined_receipt_email_with_pdf_attachment_after_confirmed_paid_booking(settings):
    settings.EMAIL_PROVIDER = "fake"
    booking, _session, _ledger = _confirm_paid_booking("combined-email")

    from bookings.services.notification_delivery import BookingNotificationDeliveryService, build_notification_email

    notification = BookingNotification.objects.get(booking=booking)
    assert notification.notification_type == "booking_confirmed_with_receipt"
    payload = build_notification_email(notification)
    assert "Booking confirmed and payment received" in payload.subject
    assert "http" not in payload.html.lower()
    assert payload.attachments == []

    result = BookingNotificationDeliveryService.send_pending(limit=10)
    notification.refresh_from_db()
    sent_payload = build_notification_email(notification)
    assert result.sent == 1
    assert len(sent_payload.attachments) == 1
    assert sent_payload.attachments[0]["filename"].endswith(".pdf")
    assert sent_payload.attachments[0]["content_type"] == "application/pdf"


@pytest.mark.django_db(transaction=True)
def test_pending_failed_or_manual_review_states_do_not_create_combined_email():
    pending_booking = _held_booking(key="combined-pending")
    _contract_service().create_checkout_for_held_booking(
        booking_public_id=pending_booking.public_id,
        idempotency_key="combined-pending-checkout",
    )
    failed_booking = _held_booking(key="combined-failed")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=failed_booking.public_id,
        idempotency_key="combined-failed-checkout",
    )
    from checkout.models import CheckoutSession

    _contract_service().fail_booking_after_payment_failure(
        checkout_session=CheckoutSession.objects.get(id=checkout["checkout_public_id"]),
        failure_reason="provider_failed",
    )
    assert (
        BookingNotification.objects.filter(
            booking__in=[pending_booking, failed_booking],
            notification_type="booking_confirmed_with_receipt",
        ).count()
        == 0
    )
