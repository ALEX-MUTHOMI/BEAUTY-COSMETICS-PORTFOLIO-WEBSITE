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
def test_checkout_billing_rollback_does_not_leave_paid_checkout_without_ledger(
    monkeypatch,
):
    customer = User.objects.create_user(email="rollback-pressure@beauty.com", phone_number="+254712640002")
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Rollback pressure",
        "booking_candidate",
        "rollback-pressure",
        "rollback-pressure-idem",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "rollback-pressure-stk")

    def explode(*args, **kwargs):
        raise RuntimeError("ledger unavailable")

    monkeypatch.setattr("checkout.services.record_successful_checkout_payment", explode)

    with pytest.raises(RuntimeError):
        process_mpesa_callback(
            {
                "CheckoutRequestID": attempt.provider_request_id,
                "MerchantRequestID": attempt.merchant_request_id,
                "ResultCode": 0,
                "Amount": "100.00",
                "MpesaReceiptNumber": "QROLLBACK",
            },
            remote_addr="127.0.0.1",
            correlation_id="rollback-pressure-correlation",
        )

    session.refresh_from_db()
    assert session.status == CheckoutSession.Status.STK_SENT
    assert LedgerTransaction.objects.count() == 0
    assert MpesaWebhookInbox.objects.get().processing_status == MpesaWebhookInbox.Status.FAILED
