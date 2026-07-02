from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from checkout.models import MpesaWebhookInbox
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
@pytest.mark.load
def test_callback_processing_exception_persists_failed_inbox_state(monkeypatch):
    customer = User.objects.create_user(email="callback-failure@aesthetic-os.test", phone_number="+254712620006")
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Callback failure",
        "booking_candidate",
        "callback-failure",
        "callback-failure-idem",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "callback-failure-stk")
    payload = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "100.00",
        "MpesaReceiptNumber": "QCALLBACKFAIL",
    }

    def explode(*args, **kwargs):
        raise RuntimeError("billing write unavailable")

    monkeypatch.setattr("checkout.services.record_successful_checkout_payment", explode)

    with pytest.raises(RuntimeError):
        process_mpesa_callback(
            payload,
            remote_addr="127.0.0.1",
            correlation_id="callback-failure-correlation",
        )

    inbox = MpesaWebhookInbox.objects.get()
    assert inbox.processing_status == MpesaWebhookInbox.Status.FAILED
    assert inbox.correlation_id == "callback-failure-correlation"
