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
def test_failed_checkout_does_not_create_successful_ledger_credit():
    customer = User.objects.create_user(email="failure-ledger@beauty.com", phone_number="+254712300003")
    session = create_checkout_session(
        customer,
        Decimal("1700.00"),
        "KES",
        "Failure",
        "booking_candidate",
        "failure-001",
        "failure-idem-001",
    )
    attempt = initiate_mpesa_stk(session.id, "+254712300003", "failure-stk-001")

    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 1032,
            "Amount": "1700.00",
        },
        remote_addr="127.0.0.1",
    )
    session.refresh_from_db()

    assert session.status == CheckoutSession.Status.FAILED
    successful_ledgers = LedgerTransaction.objects.filter(
        external_correlation_id=str(session.id),
        status=LedgerTransaction.Status.SUCCESS,
    )
    assert successful_ledgers.count() == 0
