from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.exceptions import BillingInvariantError, BillingStateError
from billing.models import LedgerTransaction
from billing.services import create_pending_ledger_transaction, mark_ledger_success

User = get_user_model()


@pytest.fixture
def ledger():
    customer = User.objects.create_user(email="immutability@beauty.com", phone_number="+254712100002")
    return create_pending_ledger_transaction(
        customer=customer,
        amount=Decimal("900.00"),
        currency="KES",
        direction=LedgerTransaction.Direction.CREDIT,
        provider=LedgerTransaction.Provider.MPESA,
        provider_reference="ws_CO_IMMUTABLE_001",
    )


@pytest.mark.django_db
def test_direct_amount_currency_direction_provider_reference_mutation_rejected(ledger):
    mutation_cases = [
        ("amount", Decimal("901.00")),
        ("currency", "USD"),
        ("direction", LedgerTransaction.Direction.DEBIT),
        ("provider_reference_hash", "tampered-hash"),
    ]

    for field, value in mutation_cases:
        fresh = LedgerTransaction.objects.get(pk=ledger.pk)
        setattr(fresh, field, value)
        with pytest.raises(BillingInvariantError):
            fresh.save()


@pytest.mark.django_db(transaction=True)
def test_success_provider_receipt_cannot_be_silently_changed(ledger):
    ledger = mark_ledger_success(ledger.id, provider_receipt="QLOCKED001")
    ledger.provider_receipt_hash = "tampered-receipt-hash"

    with pytest.raises(BillingInvariantError):
        ledger.save()


@pytest.mark.django_db(transaction=True)
def test_direct_success_to_failed_mutation_rejected(ledger):
    ledger = mark_ledger_success(ledger.id, provider_receipt="QLOCKED002")
    ledger.status = LedgerTransaction.Status.FAILED

    with pytest.raises(BillingStateError):
        ledger.save()
