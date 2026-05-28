from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from checkout.exceptions import CheckoutValidationError
from checkout.models import MpesaWebhookInbox
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_callback_amount_mismatch_is_rejected_without_ledger_success():
    customer = User.objects.create_user(
        email="mismatch-a2@beauty.com", phone_number="+254712600005"
    )
    session = create_checkout_session(
        customer,
        Decimal("1000.00"),
        "KES",
        "Mismatch",
        "booking_candidate",
        "mismatch-a2",
        "mismatch-a2-idem",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "mismatch-a2-stk")

    with pytest.raises(CheckoutValidationError):
        process_mpesa_callback(
            {
                "CheckoutRequestID": attempt.provider_request_id,
                "MerchantRequestID": attempt.merchant_request_id,
                "ResultCode": 0,
                "Amount": "999.00",
                "MpesaReceiptNumber": "QMISMATCHA2",
            },
            remote_addr="127.0.0.1",
        )

    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id)
        ).count()
        == 0
    )
    assert (
        MpesaWebhookInbox.objects.filter(
            processing_status=MpesaWebhookInbox.Status.REJECTED
        ).count()
        == 1
    )
