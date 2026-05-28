from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from checkout.models import MpesaWebhookInbox
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_duplicate_success_callback_is_idempotent_after_checkout_paid():
    customer = User.objects.create_user(
        email="duplicate-success-a2@beauty.com", phone_number="+254712600008"
    )
    session = create_checkout_session(
        customer,
        Decimal("1000.00"),
        "KES",
        "Duplicate",
        "booking_candidate",
        "duplicate-a2",
        "duplicate-a2-idem",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "duplicate-a2-stk")
    payload = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "1000.00",
        "MpesaReceiptNumber": "QDUPA2",
    }

    first = process_mpesa_callback(payload, remote_addr="127.0.0.1")
    duplicate = process_mpesa_callback(payload, remote_addr="127.0.0.1")

    assert first.inbox.processing_status == MpesaWebhookInbox.Status.PROCESSED
    assert duplicate.inbox.processing_status == MpesaWebhookInbox.Status.DUPLICATE
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id)
        ).count()
        == 1
    )
