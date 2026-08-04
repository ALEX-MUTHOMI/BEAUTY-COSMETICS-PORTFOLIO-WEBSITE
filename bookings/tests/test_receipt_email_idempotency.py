import pytest

from billing.services import record_successful_checkout_payment
from bookings.models import BookingNotification, BookingReceipt
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db(transaction=True)
def test_duplicate_confirmation_creates_one_receipt_and_one_combined_email_outbox_row():
    booking = _held_booking(key="receipt-email-idem")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="receipt-email-idem-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="provider-receipt-email-idem",
        provider_receipt="receipt-receipt-email-idem",
    )

    for _index in range(5):
        _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    assert BookingReceipt.objects.filter(booking=booking).count() == 1
    assert (
        BookingNotification.objects.filter(
            booking=booking,
            notification_type="booking_confirmed_with_receipt",
        ).count()
        == 1
    )
