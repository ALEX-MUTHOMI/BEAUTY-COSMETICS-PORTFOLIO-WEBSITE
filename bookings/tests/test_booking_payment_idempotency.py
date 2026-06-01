from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from billing.services import record_successful_checkout_payment
from bookings.models import Booking, BookingFinancialHistory
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


@pytest.mark.django_db
def test_repeated_checkout_requests_for_same_booking_return_same_checkout_session():
    booking = _held_booking(key="idem-checkout-hold")

    responses = [
        _contract_service().create_checkout_for_held_booking(
            booking_public_id=booking.public_id,
            idempotency_key="idem-checkout-key",
        )
        for _ in range(10)
    ]

    assert len({response["checkout_public_id"] for response in responses}) == 1
    assert CheckoutSession.objects.count() == 1
    assert len(str(responses[-1])) < 900


@pytest.mark.django_db
def test_same_checkout_idempotency_key_for_different_booking_is_rejected_generically():
    first = _held_booking(key="first-idem-hold")
    second = _held_booking(
        starts_at=datetime(2026, 6, 1, 10, 0, tzinfo=ZoneInfo("Africa/Nairobi")), key="second-idem-hold"
    )
    _contract_service().create_checkout_for_held_booking(
        booking_public_id=first.public_id,
        idempotency_key="shared-checkout-key",
    )

    with pytest.raises(ValidationError) as exc:
        _contract_service().create_checkout_for_held_booking(
            booking_public_id=second.public_id,
            idempotency_key="shared-checkout-key",
        )

    assert "unable to process" in str(exc.value).lower()
    assert str(second.id) not in str(exc.value)
    assert CheckoutSession.objects.count() == 1


@pytest.mark.django_db
def test_duplicate_confirmation_history_is_not_created_by_replay():
    booking = _held_booking(key="history-idempotent")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="history-idempotent-checkout",
    )
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=session.id,
        amount=session.amount_snapshot,
        currency=session.currency,
        provider_reference="history-idempotent-provider",
        provider_receipt="history-idempotent-receipt",
    )

    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    booking.refresh_from_db()
    assert booking.status == Booking.Status.CONFIRMED
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="booking_confirmed").count() == 1
