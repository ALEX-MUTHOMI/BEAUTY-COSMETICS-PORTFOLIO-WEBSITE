from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from billing.services import record_successful_checkout_payment

User = get_user_model()


@pytest.mark.django_db(transaction=True)
@pytest.mark.load
def test_one_thousand_successful_checkout_outcomes_create_one_ledger_each():
    customer = User.objects.create_user(email="ledger-storm@beauty.com", phone_number="+254712610002")

    for index in range(1000):
        record_successful_checkout_payment(
            customer=customer,
            checkout_session_id=f"ledger-storm-checkout-{index}",
            amount=Decimal("100.00"),
            currency="KES",
            provider_reference=f"ledger-storm-provider-{index}",
            provider_receipt=f"QSTORM{index:04d}",
            raw_payload={"CheckoutRequestID": f"ledger-storm-provider-{index}"},
            correlation_id=f"ledger-storm-correlation-{index}",
        )

    assert LedgerTransaction.objects.filter(status=LedgerTransaction.Status.SUCCESS).count() == 1000
    assert (
        LedgerTransaction.objects.filter(status=LedgerTransaction.Status.SUCCESS)
        .values("external_correlation_id")
        .distinct()
        .count()
        == 1000
    )
