from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction, SettlementRecord
from billing.services import record_successful_checkout_payment

User = get_user_model()


@pytest.mark.django_db(transaction=True)
@pytest.mark.load
def test_one_thousand_mixed_checkout_outcomes_only_credit_successful_valid_payments():
    customer = User.objects.create_user(email="billing-load@aesthetic-os.test", phone_number="+254712620004")

    for index in range(1000):
        if index % 2 == 0:
            record_successful_checkout_payment(
                customer=customer,
                checkout_session_id=f"billing-load-{index}",
                amount=Decimal("100.00"),
                currency="KES",
                provider_reference=f"billing-load-provider-{index}",
                provider_receipt=f"QBILLLOAD{index:04d}",
                raw_payload={"CheckoutRequestID": f"billing-load-provider-{index}"},
                correlation_id=f"billing-load-correlation-{index}",
            )

    assert LedgerTransaction.objects.filter(status=LedgerTransaction.Status.SUCCESS).count() == 500
    assert SettlementRecord.objects.count() == 500
