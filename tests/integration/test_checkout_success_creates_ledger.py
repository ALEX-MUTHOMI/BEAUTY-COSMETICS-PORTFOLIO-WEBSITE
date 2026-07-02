from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_paid_checkout_creates_exactly_one_successful_ledger_transaction():
    customer = User.objects.create_user(email="success-ledger@aesthetic-os.test", phone_number="+254712300002")
    session = create_checkout_session(
        customer,
        Decimal("1700.00"),
        "KES",
        "Success",
        "booking_candidate",
        "success-001",
        "success-idem-001",
    )
    attempt = initiate_mpesa_stk(session.id, "+254712300002", "success-stk-001")

    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 0,
            "Amount": "1700.00",
            "MpesaReceiptNumber": "QSUCCESS001",
        },
        remote_addr="127.0.0.1",
    )

    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id),
            status=LedgerTransaction.Status.SUCCESS,
        ).count()
        == 1
    )
