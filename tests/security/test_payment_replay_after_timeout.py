from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from billing.models import LedgerTransaction
from checkout.models import CheckoutAttempt
from checkout.providers.base import ProviderTimeout
from checkout.providers.fake_mpesa import FakeMpesaProvider
from checkout.services import (
    create_checkout_session,
    initiate_mpesa_stk,
    process_mpesa_callback,
)

User = get_user_model()


class TimeoutOnceProvider(FakeMpesaProvider):
    def __init__(self):
        super().__init__()
        self.calls = 0

    def initiate_stk_push(self, *args, **kwargs):
        self.calls += 1
        if self.calls == 1:
            raise ProviderTimeout("timeout")
        return super().initiate_stk_push(*args, **kwargs)


@pytest.mark.django_db(transaction=True)
def test_retry_after_provider_timeout_does_not_double_credit():
    customer = User.objects.create_user(email="timeout-replay@beauty.com", phone_number="+254712740003")
    session = create_checkout_session(
        customer,
        Decimal("170.00"),
        "KES",
        "Timeout replay",
        "booking_candidate",
        "timeout-replay",
        "timeout-replay-session",
    )
    provider = TimeoutOnceProvider()

    with pytest.raises(ProviderTimeout):
        initiate_mpesa_stk(
            session.id,
            customer.phone_number,
            "timeout-replay-stk",
            provider=provider,
        )
    attempt = initiate_mpesa_stk(session.id, customer.phone_number, "timeout-replay-stk", provider=provider)

    payload = provider.simulate_callback(attempt.provider_request_id, amount="170.00", receipt="QTIMEOUTREPLAY")
    for _ in range(10):
        process_mpesa_callback(payload, remote_addr="127.0.0.1")

    assert CheckoutAttempt.objects.filter(checkout_session=session).count() == 1
    assert LedgerTransaction.objects.filter(external_correlation_id=str(session.id)).count() == 1
