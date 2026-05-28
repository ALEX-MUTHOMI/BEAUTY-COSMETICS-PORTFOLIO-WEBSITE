from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from billing.services import create_pending_ledger_transaction

User = get_user_model()


@pytest.mark.django_db
def test_gdpr_anonymization_preserves_accounting_integrity_without_raw_provider_ids():
    customer = User.objects.create_user(
        email="gdpr-ledger@beauty.com", phone_number="+254712100006"
    )
    ledger = create_pending_ledger_transaction(
        customer,
        Decimal("700.00"),
        "KES",
        LedgerTransaction.Direction.CREDIT,
        LedgerTransaction.Provider.MPESA,
        "ws_CO_GDPR_001",
    )

    customer.anonymize()
    ledger.refresh_from_db()

    assert ledger.amount == Decimal("700.00")
    assert ledger.currency == "KES"
    assert ledger.provider_reference_hash
    assert "ws_CO_GDPR_001" not in str(ledger.__dict__)
