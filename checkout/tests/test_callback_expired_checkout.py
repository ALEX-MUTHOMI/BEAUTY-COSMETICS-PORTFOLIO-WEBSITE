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
def test_expired_checkout_success_callback_records_ledger_without_paid_transition():
    customer = User.objects.create_user(email="expired-a2@aesthetic-os.test", phone_number="+254712600006")
    session = create_checkout_session(
        customer,
        Decimal("1000.00"),
        "KES",
        "Expired",
        "booking_candidate",
        "expired-a2",
        "expired-a2-idem",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "expired-a2-stk")
    CheckoutSession.objects.filter(pk=session.pk).update(status=CheckoutSession.Status.EXPIRED)

    result = process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 0,
            "Amount": "1000.00",
            "MpesaReceiptNumber": "QEXPIREDA2",
        },
        remote_addr="127.0.0.1",
    )

    session.refresh_from_db()
    assert result.session is not None
    assert session.status == CheckoutSession.Status.EXPIRED
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id),
            status=LedgerTransaction.Status.SUCCESS,
        ).count()
        == 1
    )
