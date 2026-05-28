from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from checkout.models import CheckoutAttempt, CheckoutSession
from checkout.providers.fake_mpesa import FakeMpesaProvider
from checkout.services import create_checkout_session, initiate_mpesa_stk

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_slow_provider_and_repeated_pay_clicks_create_one_attempt():
    customer = User.objects.create_user(
        email="latency-clicks@beauty.com", phone_number="+254712730001"
    )
    session = create_checkout_session(
        customer,
        Decimal("120.00"),
        "KES",
        "Latency repeated clicks",
        "booking_candidate",
        "latency-clicks",
        "latency-clicks-session",
    )
    provider = FakeMpesaProvider(delay_seconds=0.01)

    attempts = [
        initiate_mpesa_stk(
            session.id,
            customer.phone_number,
            "latency-same-pay-click",
            provider=provider,
        )
        for _ in range(20)
    ]

    session.refresh_from_db()
    assert session.status == CheckoutSession.Status.STK_SENT
    assert len({attempt.id for attempt in attempts}) == 1
    assert CheckoutAttempt.objects.filter(checkout_session=session).count() == 1
