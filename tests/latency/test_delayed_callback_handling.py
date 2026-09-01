from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from billing.models import LedgerTransaction
from checkout.models import CheckoutSession
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_delayed_callback_marks_paid_if_checkout_not_expired():
    customer = User.objects.create_user(email="delayed-paid@aesthetic-os.test", phone_number="+254712730004")
    session = create_checkout_session(
        customer,
        Decimal("150.00"),
        "KES",
        "Delayed callback",
        "booking_candidate",
        "delayed-paid",
        "delayed-paid-session",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "delayed-paid-stk")

    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 0,
            "Amount": "150.00",
            "MpesaReceiptNumber": "QDELAYED001",
            "ProviderTimestamp": "20260101010101",
        },
        remote_addr="127.0.0.1",
    )

    session.refresh_from_db()
    assert session.status == CheckoutSession.Status.PAID
    assert LedgerTransaction.objects.filter(external_correlation_id=str(session.id)).count() == 1


@pytest.mark.django_db(transaction=True)
def test_delayed_callback_after_expiry_cannot_mark_paid():
    """Late success records ledger for reconciliation but never revives EXPIRED → PAID."""
    customer = User.objects.create_user(email="delayed-expired@aesthetic-os.test", phone_number="+254712730005")
    session = create_checkout_session(
        customer,
        Decimal("150.00"),
        "KES",
        "Delayed expired",
        "booking_candidate",
        "delayed-expired",
        "delayed-expired-session",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "delayed-expired-stk")
    CheckoutSession.objects.filter(pk=session.pk).update(
        status=CheckoutSession.Status.EXPIRED,
        expires_at=timezone.now() - timezone.timedelta(minutes=1),
    )

    process_mpesa_callback(
        {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 0,
            "Amount": "150.00",
            "MpesaReceiptNumber": "QDELAYED002",
            "ProviderTimestamp": "20260101010101",
        },
        remote_addr="127.0.0.1",
    )

    session.refresh_from_db()
    assert session.status == CheckoutSession.Status.EXPIRED
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(session.id),
            status=LedgerTransaction.Status.SUCCESS,
        ).count()
        == 1
    )
