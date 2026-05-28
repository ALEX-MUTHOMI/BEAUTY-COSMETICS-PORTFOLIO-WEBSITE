from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.exceptions import BillingStateError
from billing.models import LedgerTransaction
from billing.services import (
    create_pending_ledger_transaction,
    mark_ledger_failed,
    mark_ledger_success,
    record_refund,
    record_reversal,
)

User = get_user_model()


@pytest.fixture
def customer():
    return User.objects.create_user(
        email="ledger-lifecycle@beauty.com", phone_number="+254712100001"
    )


def pending_ledger(customer, provider_reference):
    return create_pending_ledger_transaction(
        customer=customer,
        amount=Decimal("1000.00"),
        currency="KES",
        direction=LedgerTransaction.Direction.CREDIT,
        provider=LedgerTransaction.Provider.MPESA,
        provider_reference=provider_reference,
    )


@pytest.mark.django_db
def test_create_pending_ledger_transaction(customer):
    ledger = create_pending_ledger_transaction(
        customer=customer,
        amount=Decimal("1200.00"),
        currency="KES",
        direction=LedgerTransaction.Direction.CREDIT,
        provider=LedgerTransaction.Provider.MPESA,
        provider_reference="ws_CO_LIFECYCLE_001",
        external_correlation_id="checkout-session-001",
    )

    assert ledger.status == LedgerTransaction.Status.PENDING
    assert ledger.amount == Decimal("1200.00")
    assert ledger.currency == "KES"
    assert ledger.provider_reference_hash


@pytest.mark.django_db(transaction=True)
def test_pending_to_success_and_pending_to_failed_allowed(customer):
    success_ledger = pending_ledger(customer, "ref-success")
    failed_ledger = pending_ledger(customer, "ref-failed")

    assert (
        mark_ledger_success(success_ledger.id, provider_receipt="QREDACT001").status
        == LedgerTransaction.Status.SUCCESS
    )
    assert (
        mark_ledger_failed(failed_ledger.id, reason="provider rejected").status
        == LedgerTransaction.Status.FAILED
    )


@pytest.mark.django_db(transaction=True)
def test_invalid_success_failed_transitions_rejected(customer):
    success_ledger = pending_ledger(customer, "ref-sf")
    failed_ledger = pending_ledger(customer, "ref-fs")
    success_ledger = mark_ledger_success(
        success_ledger.id, provider_receipt="QREDACT002"
    )
    failed_ledger = mark_ledger_failed(failed_ledger.id, reason="provider rejected")

    with pytest.raises(BillingStateError):
        mark_ledger_failed(success_ledger.id, reason="illegal downgrade")

    with pytest.raises(BillingStateError):
        mark_ledger_success(failed_ledger.id, provider_receipt="QREDACT003")


@pytest.mark.django_db(transaction=True)
def test_success_reversal_and_refund_require_audited_services(customer):
    reversed_ledger = pending_ledger(customer, "ref-rev")
    refunded_ledger = pending_ledger(customer, "ref-refund")
    reversed_ledger = mark_ledger_success(
        reversed_ledger.id, provider_receipt="QREV001"
    )
    refunded_ledger = mark_ledger_success(
        refunded_ledger.id, provider_receipt="QREF001"
    )

    assert (
        record_reversal(reversed_ledger.id, reason="chargeback").status
        == LedgerTransaction.Status.REVERSED
    )
    assert (
        record_refund(refunded_ledger.id, reason="customer refund").status
        == LedgerTransaction.Status.REFUNDED
    )
