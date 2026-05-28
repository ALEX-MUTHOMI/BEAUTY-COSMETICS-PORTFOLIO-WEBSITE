from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from checkout.models import CheckoutSession, MpesaWebhookInbox
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
@pytest.mark.load
def test_one_thousand_duplicate_callbacks_for_one_checkout_credit_once():
    customer = User.objects.create_user(
        email="webhook-storm@beauty.com", phone_number="+254712620002"
    )
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Webhook storm",
        "booking_candidate",
        "webhook-storm",
        "webhook-storm-idem",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "webhook-storm-stk")
    payload = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "100.00",
        "MpesaReceiptNumber": "QWEBHOOKSTORM",
    }

    statuses = [
        process_mpesa_callback(payload, remote_addr="127.0.0.1").inbox.processing_status
        for _ in range(1000)
    ]

    session.refresh_from_db()
    assert session.status == CheckoutSession.Status.PAID
    assert statuses.count(MpesaWebhookInbox.Status.PROCESSED) == 1
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id)
        ).count()
        == 1
    )
