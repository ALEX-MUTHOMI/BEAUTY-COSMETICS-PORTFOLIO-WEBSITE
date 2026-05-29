from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import close_old_connections

from billing.models import LedgerTransaction
from checkout.models import CheckoutSession, MpesaWebhookInbox
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_concurrent_duplicate_callbacks_do_not_double_credit():
    customer = User.objects.create_user(email="parallel-callback@beauty.com", phone_number="+254712300004")
    session = create_checkout_session(
        customer,
        Decimal("3100.00"),
        "KES",
        "Parallel",
        "booking_candidate",
        "parallel-001",
        "parallel-idem-001",
    )
    attempt = initiate_mpesa_stk(session.id, "+254712300004", "parallel-stk-001")
    payload = {
        "CheckoutRequestID": attempt.provider_request_id,
        "MerchantRequestID": attempt.merchant_request_id,
        "ResultCode": 0,
        "Amount": "3100.00",
        "MpesaReceiptNumber": "QPARALLEL001",
    }

    def callback():
        close_old_connections()
        try:
            return process_mpesa_callback(payload, remote_addr="127.0.0.1").inbox.processing_status
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(callback) for _ in range(10)]
        statuses = [future.result(timeout=15) for future in as_completed(futures)]

    session.refresh_from_db()
    assert session.status == CheckoutSession.Status.PAID
    assert statuses.count(MpesaWebhookInbox.Status.PROCESSED) == 1
    successful_ledgers = LedgerTransaction.objects.filter(
        external_correlation_id=str(session.id),
        status=LedgerTransaction.Status.SUCCESS,
    )
    assert successful_ledgers.count() == 1
