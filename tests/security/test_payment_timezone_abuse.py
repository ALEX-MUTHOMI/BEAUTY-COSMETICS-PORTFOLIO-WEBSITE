from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from billing.models import LedgerTransaction
from checkout.exceptions import CheckoutStateError
from checkout.models import CheckoutSession
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_future_provider_timestamp_cannot_bypass_cancelled_checkout_state():
    customer = User.objects.create_user(email="tz-abuse@aesthetic-os.test", phone_number="+254712720001")
    session = create_checkout_session(
        customer,
        Decimal("80.00"),
        "KES",
        "Timezone abuse",
        "booking_candidate",
        "tz-abuse-001",
        "tz-abuse-idem-001",
    )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "tz-abuse-stk-001")
    CheckoutSession.objects.filter(pk=session.pk).update(
        status=CheckoutSession.Status.CANCELLED,
        expires_at=timezone.now() + timezone.timedelta(days=1),
    )

    with pytest.raises(CheckoutStateError):
        process_mpesa_callback(
            {
                "CheckoutRequestID": attempt.provider_request_id,
                "MerchantRequestID": attempt.merchant_request_id,
                "ResultCode": 0,
                "Amount": "80.00",
                "MpesaReceiptNumber": "QTZABUSE001",
                "ProviderTimestamp": "20991231235959",
            },
            remote_addr="127.0.0.1",
        )

    assert LedgerTransaction.objects.filter(external_correlation_id=str(session.id)).count() == 0
