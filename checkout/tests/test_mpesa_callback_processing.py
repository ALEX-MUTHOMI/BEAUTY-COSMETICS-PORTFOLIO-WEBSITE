from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from checkout.exceptions import CheckoutStateError, CheckoutValidationError
from checkout.models import CheckoutSession, MpesaWebhookInbox
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.fixture
def stk_session():
    customer = User.objects.create_user(
        email="callback@beauty.com", phone_number="+254712200004"
    )
    session = create_checkout_session(
        customer,
        Decimal("2100.00"),
        "KES",
        "Callback checkout",
        "booking_candidate",
        "callback-001",
        "callback-idem-001",
    )
    initiate_mpesa_stk(
        session.id, phone_number="+254712200004", idempotency_key="callback-stk-001"
    )
    return session


@pytest.mark.django_db(transaction=True)
def test_successful_webhook_marks_checkout_paid_once_and_creates_one_ledger(
    stk_session,
):
    payload = {
        "CheckoutRequestID": stk_session.attempts.first().provider_request_id,
        "MerchantRequestID": "merchant-callback-001",
        "ResultCode": 0,
        "Amount": "2100.00",
        "MpesaReceiptNumber": "QCALLBACK001",
    }

    result = process_mpesa_callback(payload, remote_addr="127.0.0.1")
    duplicate = process_mpesa_callback(payload, remote_addr="127.0.0.1")
    stk_session.refresh_from_db()

    assert result.session.status == CheckoutSession.Status.PAID
    assert duplicate.inbox.processing_status == MpesaWebhookInbox.Status.DUPLICATE
    assert (
        LedgerTransaction.objects.filter(
            external_correlation_id=str(stk_session.id)
        ).count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
def test_failed_webhook_marks_checkout_failed_without_credit(stk_session):
    payload = {
        "CheckoutRequestID": stk_session.attempts.first().provider_request_id,
        "MerchantRequestID": "merchant-callback-002",
        "ResultCode": 1032,
        "Amount": "2100.00",
    }

    result = process_mpesa_callback(payload, remote_addr="127.0.0.1")
    stk_session.refresh_from_db()

    assert result.session.status == CheckoutSession.Status.FAILED
    successful_ledgers = LedgerTransaction.objects.filter(
        external_correlation_id=str(stk_session.id),
        status=LedgerTransaction.Status.SUCCESS,
    )
    assert successful_ledgers.count() == 0


@pytest.mark.django_db(transaction=True)
def test_mismatched_or_unknown_checkout_request_rejected(stk_session):
    with pytest.raises(CheckoutValidationError):
        process_mpesa_callback(
            {
                "CheckoutRequestID": stk_session.attempts.first().provider_request_id,
                "MerchantRequestID": "merchant-callback-003",
                "ResultCode": 0,
                "Amount": "9999.00",
                "MpesaReceiptNumber": "QMISMATCH001",
            },
            remote_addr="127.0.0.1",
        )

    with pytest.raises(CheckoutValidationError):
        process_mpesa_callback(
            {
                "CheckoutRequestID": "ws_CO_UNKNOWN",
                "MerchantRequestID": "merchant-callback-004",
                "ResultCode": 0,
                "Amount": "2100.00",
                "MpesaReceiptNumber": "QUNKNOWN001",
            },
            remote_addr="127.0.0.1",
        )


@pytest.mark.django_db(transaction=True)
def test_expired_or_cancelled_checkout_rejects_success_callback(stk_session):
    stk_session.status = CheckoutSession.Status.EXPIRED
    stk_session.save(update_fields=["status", "updated_at"])

    with pytest.raises(CheckoutStateError):
        process_mpesa_callback(
            {
                "CheckoutRequestID": stk_session.attempts.first().provider_request_id,
                "MerchantRequestID": "merchant-callback-005",
                "ResultCode": 0,
                "Amount": "2100.00",
                "MpesaReceiptNumber": "QEXPIRED001",
            },
            remote_addr="127.0.0.1",
        )
