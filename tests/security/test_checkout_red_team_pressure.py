from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from checkout.exceptions import CheckoutValidationError
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_red_team_amount_mismatch_cannot_force_success_credit():
    customer = User.objects.create_user(email="checkout-pressure@beauty.com", phone_number="+254712630002")
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Pressure",
        "booking_candidate",
        "checkout-pressure",
        "checkout-pressure-idem",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "checkout-pressure-stk")

    with pytest.raises(CheckoutValidationError):
        process_mpesa_callback(
            {
                "CheckoutRequestID": attempt.provider_request_id,
                "MerchantRequestID": attempt.merchant_request_id,
                "ResultCode": 0,
                "Amount": "101.00",
                "MpesaReceiptNumber": "QPRESSURE002",
            },
            remote_addr="127.0.0.1",
        )

    assert LedgerTransaction.objects.count() == 0
