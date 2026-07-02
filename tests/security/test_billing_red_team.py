from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.exceptions import BillingInvariantError
from billing.models import LedgerTransaction
from billing.services import create_pending_ledger_transaction, mark_ledger_success

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_red_team_ledger_mutation_and_negative_amount_attacks_are_blocked():
    customer = User.objects.create_user(email="billing-redteam@aesthetic-os.test", phone_number="+254712400003")
    with pytest.raises(ValueError):
        create_pending_ledger_transaction(
            customer,
            Decimal("-1.00"),
            "KES",
            LedgerTransaction.Direction.CREDIT,
            LedgerTransaction.Provider.MPESA,
            "negative-ref",
        )

    ledger = create_pending_ledger_transaction(
        customer,
        Decimal("600.00"),
        "KES",
        LedgerTransaction.Direction.CREDIT,
        LedgerTransaction.Provider.MPESA,
        "immutable-ref",
    )
    ledger.amount = Decimal("999999.00")
    with pytest.raises(BillingInvariantError):
        ledger.save()


@pytest.mark.django_db(transaction=True)
def test_red_team_successful_provider_reference_mutation_is_blocked():
    customer = User.objects.create_user(email="billing-redteam-ref@aesthetic-os.test", phone_number="+254712400004")
    ledger = create_pending_ledger_transaction(
        customer,
        Decimal("600.00"),
        "KES",
        LedgerTransaction.Direction.CREDIT,
        LedgerTransaction.Provider.MPESA,
        "success-ref",
    )
    ledger = mark_ledger_success(ledger.id, provider_receipt="QORIGINAL001")
    ledger.provider_receipt_hash = "attacker-mutated-receipt-hash"

    with pytest.raises(BillingInvariantError):
        ledger.save()
