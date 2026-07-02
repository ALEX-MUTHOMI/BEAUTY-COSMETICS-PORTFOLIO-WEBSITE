from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from checkout.models import CheckoutAttempt
from checkout.providers.fake_mpesa import FakeMpesaProvider
from checkout.services import create_checkout_session, initiate_mpesa_stk

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_customer_network_retry_with_same_key_is_resumable_and_idempotent():
    customer = User.objects.create_user(email="customer-network@aesthetic-os.test", phone_number="+254712760001")
    session = create_checkout_session(
        customer,
        Decimal("210.00"),
        "KES",
        "Customer network retry",
        "booking_candidate",
        "customer-network",
        "customer-network-session",
    )
    provider = FakeMpesaProvider(delay_seconds=0.01)

    first = initiate_mpesa_stk(
        session.id,
        customer.phone_number,
        "customer-network-stk",
        provider=provider,
    )
    recovered = initiate_mpesa_stk(
        session.id,
        customer.phone_number,
        "customer-network-stk",
        provider=provider,
    )

    assert first.id == recovered.id
    assert CheckoutAttempt.objects.filter(checkout_session=session).count() == 1
