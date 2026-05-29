from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import SettlementRecord
from billing.services import record_successful_checkout_payment

User = get_user_model()


@pytest.mark.django_db(transaction=True)
@pytest.mark.load
def test_duplicate_success_outcomes_create_single_settlement_record():
    customer = User.objects.create_user(email="settlement-storm@beauty.com", phone_number="+254712610003")

    for index in range(1000):
        record_successful_checkout_payment(
            customer=customer,
            checkout_session_id="settlement-storm-checkout",
            amount=Decimal("100.00"),
            currency="KES",
            provider_reference="settlement-storm-provider",
            provider_receipt=f"QSETTLE{index:04d}",
            raw_payload={"CheckoutRequestID": "settlement-storm-provider"},
            correlation_id=f"settlement-storm-correlation-{index}",
        )

    assert SettlementRecord.objects.count() == 1
