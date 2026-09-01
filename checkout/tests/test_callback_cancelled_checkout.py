from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from checkout.models import CheckoutSession
from checkout.services import (
    cancel_checkout_session,
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_cancelled_checkout_success_callback_records_ledger_without_paid_transition():
    customer = User.objects.create_user(email="cancelled-a2@aesthetic-os.test", phone_number="+254712600007")
    session = create_checkout_session(
        customer,
        Decimal("1000.00"),
        "KES",
        "Cancelled",
        "booking_candidate",
        "cancelled-a2",
        "cancelled-a2-idem",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "cancelled-a2-stk")
    cancel_checkout_session(session.id)

    result = process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 0,
            "Amount": "1000.00",
            "MpesaReceiptNumber": "QCANCELLEDA2",
        },
        remote_addr="127.0.0.1",
    )

    session.refresh_from_db()
    assert result.session is not None
    assert session.status == CheckoutSession.Status.CANCELLED
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id),
            status=LedgerTransaction.Status.SUCCESS,
        ).count()
        == 1
    )
