from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from billing.models import LedgerTransaction
from billing.services import create_pending_ledger_transaction, mark_ledger_failed, record_successful_checkout_payment
from bookings.models import Booking
from bookings.tests.factories import create_booking
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking
from checkout.models import CheckoutSession


def _session_for_booking(booking, key):
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key=key,
    )
    return CheckoutSession.objects.get(id=checkout["checkout_public_id"])


def _successful_ledger(session, amount=None, currency=None, correlation=None):
    ledger, _created = record_successful_checkout_payment(
        customer=session.customer,
        checkout_session_id=correlation or session.id,
        amount=amount or session.amount_snapshot,
        currency=currency or session.currency,
        provider_reference=f"provider-{session.id}",
        provider_receipt=f"receipt-{session.id}",
    )
    return ledger


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("status", ["pending", "failed"])
def test_non_success_ledger_does_not_confirm_booking(status):
    booking = _held_booking(key=f"ledger-status-{status}")
    session = _session_for_booking(booking, f"ledger-status-{status}-checkout")
    ledger = create_pending_ledger_transaction(
        customer=session.customer,
        amount=session.amount_snapshot,
        currency=session.currency,
        direction=LedgerTransaction.Direction.CREDIT,
        provider=LedgerTransaction.Provider.MPESA,
        provider_reference=f"provider-{status}",
        external_correlation_id=str(session.id),
    )
    if status == "failed":
        ledger = mark_ledger_failed(ledger.id, "provider failure")

    with pytest.raises(ValidationError):
        _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_PENDING


@pytest.mark.django_db(transaction=True)
def test_wrong_amount_and_currency_do_not_confirm_booking():
    booking = _held_booking(key="ledger-amount-currency")
    session = _session_for_booking(booking, "ledger-amount-currency-checkout")

    wrong_amount = _successful_ledger(session, amount=session.amount_snapshot + Decimal("1.00"))
    with pytest.raises(ValidationError):
        _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=wrong_amount)
    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_PENDING

    wrong_currency = _successful_ledger(session, currency="USD", correlation=f"{session.id}-currency")
    with pytest.raises(ValidationError):
        _contract_service().confirm_booking_after_billing_success(
            checkout_session=session,
            billing_ledger=wrong_currency,
        )
    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_PENDING


@pytest.mark.django_db(transaction=True)
def test_wrong_checkout_linkage_does_not_confirm_booking():
    booking = _held_booking(key="ledger-wrong-link")
    session = _session_for_booking(booking, "ledger-wrong-link-checkout")
    ledger = _successful_ledger(session, correlation="another-checkout-session")

    with pytest.raises(ValidationError):
        _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_PENDING


@pytest.mark.django_db(transaction=True)
def test_wrong_purchasable_type_does_not_confirm_booking():
    booking = _held_booking(key="ledger-wrong-type")
    session = _session_for_booking(booking, "ledger-wrong-type-checkout")
    ledger = _successful_ledger(session)
    session.purchasable_type = "booking_candidate"
    session.save(update_fields=["purchasable_type"])

    with pytest.raises(ValidationError):
        _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    booking.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_PENDING


@pytest.mark.django_db(transaction=True)
def test_wrong_purchasable_id_does_not_confirm_another_booking():
    booking = _held_booking(key="ledger-wrong-id-original")
    session = _session_for_booking(booking, "ledger-wrong-id-checkout")
    ledger = _successful_ledger(session)

    other = create_booking(
        customer_profile=booking.customer_profile,
        service=booking.service,
        resource=booking.resource,
        starts_at=booking.starts_at.replace(hour=booking.starts_at.hour + 2),
        ends_at=booking.ends_at.replace(hour=booking.ends_at.hour + 2),
        status=Booking.Status.PAYMENT_PENDING,
        idempotency_key="ledger-wrong-id-other",
    )
    session.purchasable_id = str(other.id)
    session.save(update_fields=["purchasable_id"])

    with pytest.raises(ValidationError):
        _contract_service().confirm_booking_after_billing_success(checkout_session=session, billing_ledger=ledger)

    booking.refresh_from_db()
    other.refresh_from_db()
    assert booking.status == Booking.Status.PAYMENT_PENDING
    assert other.status == Booking.Status.PAYMENT_PENDING
