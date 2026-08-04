from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import FinancialAuditEvent
from billing.services import record_successful_checkout_payment

User = get_user_model()


@pytest.mark.django_db(transaction=True)
@pytest.mark.load
def test_duplicate_success_outcomes_create_single_success_audit_event():
    customer = User.objects.create_user(email="audit-storm@aesthetic-os.test", phone_number="+254712610004")

    for index in range(1000):
        record_successful_checkout_payment(
            customer=customer,
            checkout_session_id="audit-storm-checkout",
            amount=Decimal("100.00"),
            currency="KES",
            provider_reference="audit-storm-provider",
            provider_receipt=f"QAUDIT{index:04d}",
            raw_payload={"CheckoutRequestID": "audit-storm-provider"},
            correlation_id=f"audit-storm-correlation-{index}",
        )

    assert FinancialAuditEvent.objects.filter(event_type="LEDGER_SUCCESS").count() == 1
