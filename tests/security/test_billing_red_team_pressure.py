from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.exceptions import BillingInvariantError
from billing.models import LedgerTransaction
from billing.services import create_pending_ledger_transaction, mark_ledger_success

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_red_team_cannot_mutate_success_receipt_under_pressure():
    customer = User.objects.create_user(email="billing-pressure@aesthetic-os.test", phone_number="+254712630001")
    ledger = create_pending_ledger_transaction(
        customer=customer,
        amount=Decimal("100.00"),
        currency="KES",
        direction=LedgerTransaction.Direction.CREDIT,
        provider=LedgerTransaction.Provider.MPESA,
        provider_reference="billing-pressure-provider",
        external_correlation_id="billing-pressure-checkout",
    )
    ledger = mark_ledger_success(ledger.id, provider_receipt="QPRESSURE001")

    ledger.provider_receipt_hash = "attacker-mutated-receipt"
    with pytest.raises(BillingInvariantError):
        ledger.save()
