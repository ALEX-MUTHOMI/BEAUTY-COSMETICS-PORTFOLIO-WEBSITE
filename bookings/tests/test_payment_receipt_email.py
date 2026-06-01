import pytest

from billing.services import record_successful_checkout_payment
from bookings.models import BookingNotification
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


def _confirm(key):
    booking = _held_booking(key=key)
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key=f"{key}-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference=f"provider-{key}",
        provider_receipt=f"receipt-{key}",
    )
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)
    return booking


@pytest.mark.django_db(transaction=True)
def test_payment_receipt_email_outbox_created_once_after_confirmed_paid_booking():
    booking = _confirm("payment-email")
    receipts = BookingNotification.objects.filter(
        booking=booking,
        notification_type="booking_confirmed_with_receipt",
        channel=BookingNotification.Channel.EMAIL,
        status=BookingNotification.Status.PENDING,
    )
    assert receipts.count() == 1
    assert receipts.get().receipt == booking.receipt


@pytest.mark.django_db(transaction=True)
def test_payment_receipt_email_contains_secure_receipt_link_and_no_raw_provider_ids():
    booking = _confirm("payment-email-body")
    notification = BookingNotification.objects.get(booking=booking, notification_type="booking_confirmed_with_receipt")

    from bookings.services.notification_delivery import build_notification_email

    email = build_notification_email(notification)
    surface = f"{email.subject} {email.html} {email.text}"
    assert "Booking confirmed and payment received" in email.subject
    assert booking.receipt.receipt_number in surface
    assert "2500.00" in surface
    assert "M-Pesa" in surface
    assert "attached" in surface.lower()
    assert "grace@example.com" not in surface
    assert "+254712345678" not in surface
    assert notification.receipt.checkout_session_id not in surface
    assert notification.receipt.billing_ledger_id not in surface
