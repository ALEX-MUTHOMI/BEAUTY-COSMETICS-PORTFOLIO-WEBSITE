from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from checkout.models import CheckoutSession
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_failed_callback_contract_does_not_credit_billing():
    customer = User.objects.create_user(email="failed-contract@beauty.com", phone_number="+254712640004")
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Failed contract",
        "booking_candidate",
        "failed-contract",
        "failed-contract-idem",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "failed-contract-stk")

    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 1032,
            "Amount": "100.00",
        },
        remote_addr="127.0.0.1",
    )

    session.refresh_from_db()
    assert session.status == CheckoutSession.Status.FAILED
    assert LedgerTransaction.objects.count() == 0
