from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.exceptions import BillingInvariantError
from billing.models import LedgerTransaction
from billing.services import create_pending_ledger_transaction, mark_ledger_success

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_successful_callback_cannot_mutate_amount_after_ledger_success():
    customer = User.objects.create_user(
        email="immutability-pressure@beauty.com", phone_number="+254712610001"
    )
    ledger = create_pending_ledger_transaction(
        customer=customer,
        amount=Decimal("1000.00"),
        currency="KES",
        direction=LedgerTransaction.Direction.CREDIT,
        provider=LedgerTransaction.Provider.MPESA,
        provider_reference="immutable-pressure-provider-ref",
        external_correlation_id="immutable-pressure-checkout",
    )
    ledger = mark_ledger_success(ledger.id, provider_receipt="QIMMUTABLEA2")

    ledger.amount = Decimal("1.00")
    with pytest.raises(BillingInvariantError):
        ledger.save()
