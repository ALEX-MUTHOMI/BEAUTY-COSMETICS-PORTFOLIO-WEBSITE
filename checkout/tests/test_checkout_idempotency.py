from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from checkout.models import CheckoutAttempt, CheckoutSession
from checkout.services import create_checkout_session, initiate_mpesa_stk

User = get_user_model()


@pytest.fixture
def customer():
    return User.objects.create_user(email="checkout-idem@aesthetic-os.test", phone_number="+254712200002")


@pytest.mark.django_db(transaction=True)
def test_idempotency_key_returns_existing_checkout_session(customer):
    kwargs = {
        "customer": customer,
        "amount": Decimal("1500.00"),
        "currency": "KES",
        "description": "Idempotent checkout",
        "purchasable_type": "booking_candidate",
        "purchasable_id": "idem-candidate-001",
        "idempotency_key": "checkout-idem-001",
    }

    first = create_checkout_session(**kwargs)
    second = create_checkout_session(**kwargs)

    assert first.id == second.id
    assert CheckoutSession.objects.filter(idempotency_key="checkout-idem-001").count() == 1


@pytest.mark.django_db(transaction=True)
def test_duplicate_stk_initiation_does_not_create_duplicate_attempts(customer):
    session = create_checkout_session(
        customer,
        Decimal("1500.00"),
        "KES",
        "STK idem",
        "booking_candidate",
        "stk-idem-001",
        "checkout-idem-stk-001",
    )

    first = initiate_mpesa_stk(session.id, phone_number="+254712200002", idempotency_key="stk-idem-key-001")
    second = initiate_mpesa_stk(session.id, phone_number="+254712200002", idempotency_key="stk-idem-key-001")

    assert first.id == second.id
    assert CheckoutAttempt.objects.filter(checkout_session=session).count() == 1
