import pytest

from billing.services import record_successful_checkout_payment
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db(transaction=True)
def test_receipt_pdf_and_email_payloads_are_bounded_and_retry_safe(settings):
    settings.EMAIL_PROVIDER = "fake"
    booking = _held_booking(key="receipt-email-latency")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="receipt-email-latency-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="provider-latency",
        provider_receipt="receipt-latency",
    )
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    from bookings.services.notification_delivery import BookingNotificationDeliveryService, build_notification_email
    from bookings.services.receipt_pdf import ReceiptPDFService

    emails = [build_notification_email(notification) for notification in booking.notifications.all()]
    assert all(len(email.html.encode()) < 20_000 for email in emails)
    assert len(ReceiptPDFService.generate_pdf(booking.receipt)) < 120_000
    assert BookingNotificationDeliveryService.send_pending(limit=1).sent == 1
    assert BookingNotificationDeliveryService.send_pending(limit=10).sent == 1
    assert BookingNotificationDeliveryService.send_pending(limit=10).sent == 0
