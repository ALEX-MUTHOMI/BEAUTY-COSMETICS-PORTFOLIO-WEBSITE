from concurrent.futures import ThreadPoolExecutor

import pytest

from billing.services import record_successful_checkout_payment
from bookings.models import Booking, BookingAuditEvent, BookingFinancialHistory
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


def _confirmed_booking(key):
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
    return booking, session, ledger


@pytest.mark.django_db(transaction=True)
def test_duplicate_success_creates_one_success_history_and_one_confirmation_audit():
    booking, session, ledger = _confirmed_booking("duplicate-history")
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)
    first_confirmed_at = Booking.objects.get(pk=booking.pk).confirmed_at
    _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    booking.refresh_from_db()
    assert booking.status == Booking.Status.CONFIRMED
    assert booking.confirmed_at == first_confirmed_at
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="payment_success").count() == 1
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="booking_confirmed").count() == 1
    assert BookingAuditEvent.objects.filter(booking=booking, new_status=Booking.Status.CONFIRMED).count() == 1


@pytest.mark.django_db(transaction=True)
def test_concurrent_duplicate_success_is_bounded():
    booking, session, ledger = _confirmed_booking("duplicate-history-concurrent")

    def confirm_once():
        _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda _index: confirm_once(), range(2)))

    booking.refresh_from_db()
    assert booking.status == Booking.Status.CONFIRMED
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="payment_success").count() == 1
    assert BookingAuditEvent.objects.filter(booking=booking, new_status=Booking.Status.CONFIRMED).count() == 1
