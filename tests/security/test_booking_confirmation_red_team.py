import pytest
from django.core.exceptions import ValidationError

from billing.services import record_successful_checkout_payment
from bookings.models import Booking, BookingFinancialHistory
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db(transaction=True)
def test_invalid_confirmation_errors_do_not_leak_pii_or_internal_ids(caplog):
    booking = _held_booking(key="b4a-redteam-leak")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="b4a-redteam-leak-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id="attacker-checkout",
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="<script>CHECKOUT-RAW</script>",
        provider_receipt="RAW-RECEIPT-123",
    )

    with pytest.raises(ValidationError) as exc:
        _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    leak_surface = f"{exc.value} {caplog.text}"
    assert "grace@example.com" not in leak_surface
    assert "+254" not in leak_surface
    assert "RAW-RECEIPT" not in leak_surface
    assert "CHECKOUT-RAW" not in leak_surface
    assert "<script" not in leak_surface
    assert str(booking.id) not in leak_surface


@pytest.mark.django_db(transaction=True)
def test_manual_review_path_does_not_generate_customer_receipt_or_email():
    booking = _held_booking(key="b4a-redteam-manual-review")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="b4a-redteam-manual-review-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    _contract_service().fail_booking_after_payment_failure(checkout_session=session, failure_reason="failed")
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="provider-manual-review",
        provider_receipt="receipt-manual-review",
    )

    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    from bookings.models import BookingNotification, BookingReceipt

    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_FAILED
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="requires_manual_review").count() == 1
    assert BookingReceipt.objects.filter(booking=booking).count() == 0
    assert BookingNotification.objects.filter(booking=booking).count() == 0
