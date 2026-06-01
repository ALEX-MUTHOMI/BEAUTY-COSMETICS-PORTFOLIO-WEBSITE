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
def test_booking_confirmation_email_outbox_created_once_after_confirmed_paid_booking():
    booking = _confirm("booking-email")
    _confirmations = BookingNotification.objects.filter(
        booking=booking,
        notification_type="booking_confirmed",
        channel=BookingNotification.Channel.EMAIL,
        status=BookingNotification.Status.PENDING,
    )
    assert _confirmations.count() == 1
    assert _confirmations.get().receipt == booking.receipt


@pytest.mark.django_db(transaction=True)
def test_booking_confirmation_email_body_is_safe_and_transactional():
    booking = _confirm("booking-email-body")
    notification = BookingNotification.objects.get(booking=booking, notification_type="booking_confirmed")

    from bookings.services.notification_delivery import build_notification_email

    email = build_notification_email(notification)
    surface = f"{email.subject} {email.html} {email.text}"
    assert "Booking confirmed" in email.subject
    assert str(booking.public_id) in surface
    assert "Confirmed" in surface
    assert "Paid" in surface
    assert "grace@example.com" not in surface
    assert "+254712345678" not in surface
    assert notification.receipt.checkout_session_id not in surface
    assert notification.receipt.billing_ledger_id not in surface
