from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from django.contrib.auth import get_user_model

from checkout.models import CheckoutAttempt, CheckoutSession
from checkout.providers.base import MpesaProviderResponse
from checkout.services import create_checkout_session, initiate_mpesa_stk

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_stk_provider_io_runs_outside_select_for_update_claim():
    """Claim creates INITIATED attempt under lock; provider runs after claim commits."""
    customer = User.objects.create_user(email="stk-lock@aesthetic-os.test", phone_number="+254712800001")
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "STK lock",
        "booking_candidate",
        "stk-lock-1",
        "stk-lock-idem",
    )

    seen_statuses = []

    def _initiate(**kwargs):
        attempt = CheckoutAttempt.objects.get(idempotency_key="stk-lock-stk")
        seen_statuses.append(attempt.status)
        assert attempt.provider_request_id.startswith("pending-co:")
        return MpesaProviderResponse(
            checkout_request_id="ws_CO_LOCK_1",
            merchant_request_id="ws_MR_LOCK_1",
        )

    provider = MagicMock()
    provider.initiate_stk_push.side_effect = _initiate

    attempt = initiate_mpesa_stk(
        session.id,
        phone_number=customer.phone_number,
        idempotency_key="stk-lock-stk",
        provider=provider,
    )

    assert seen_statuses == [CheckoutAttempt.Status.INITIATED]
    assert attempt.status == CheckoutAttempt.Status.SENT
    assert attempt.provider_request_id == "ws_CO_LOCK_1"
    session.refresh_from_db()
    assert session.status == CheckoutSession.Status.STK_SENT
    provider.initiate_stk_push.assert_called_once()
