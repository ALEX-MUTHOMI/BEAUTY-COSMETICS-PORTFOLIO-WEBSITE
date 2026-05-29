from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from checkout.exceptions import CheckoutStateError
from checkout.models import CheckoutSession
from checkout.services import (
    cancel_checkout_session,
    create_checkout_session,
    expire_checkout_session,
)
from checkout.state_machine import transition_checkout

User = get_user_model()


@pytest.fixture
def customer():
    return User.objects.create_user(email="checkout-lifecycle@beauty.com", phone_number="+254712200001")


@pytest.mark.django_db
def test_create_checkout_session_with_valid_decimal_amount(customer):
    session = create_checkout_session(
        customer=customer,
        amount=Decimal("1800.00"),
        currency="KES",
        description="Facial deposit",
        purchasable_type="booking_candidate",
        purchasable_id="candidate-001",
        idempotency_key="idem-lifecycle-001",
    )

    assert session.status == CheckoutSession.Status.CREATED
    assert session.amount_snapshot == Decimal("1800.00")
    assert session.expires_at > timezone.now()


@pytest.mark.django_db
def test_reject_zero_negative_and_float_amounts(customer):
    invalid_amounts = [Decimal("0.00"), Decimal("-1.00"), 1200.10]

    for amount in invalid_amounts:
        with pytest.raises(ValueError):
            create_checkout_session(
                customer=customer,
                amount=amount,
                currency="KES",
                description="Invalid",
                purchasable_type="booking_candidate",
                purchasable_id="candidate-invalid",
                idempotency_key=f"idem-invalid-{amount}",
            )


@pytest.mark.django_db(transaction=True)
def test_checkout_state_machine_terminal_states(customer):
    paid = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Paid",
        "booking_candidate",
        "paid-001",
        "idem-paid-001",
    )
    failed = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Failed",
        "booking_candidate",
        "failed-001",
        "idem-failed-001",
    )

    transition_checkout(paid, CheckoutSession.Status.PAYMENT_PENDING)
    transition_checkout(paid, CheckoutSession.Status.STK_SENT)
    transition_checkout(paid, CheckoutSession.Status.PAID)
    transition_checkout(failed, CheckoutSession.Status.PAYMENT_PENDING)
    transition_checkout(failed, CheckoutSession.Status.STK_SENT)
    transition_checkout(failed, CheckoutSession.Status.FAILED)

    with pytest.raises(CheckoutStateError):
        transition_checkout(paid, CheckoutSession.Status.FAILED)
    with pytest.raises(CheckoutStateError):
        transition_checkout(failed, CheckoutSession.Status.PAID)


@pytest.mark.django_db(transaction=True)
def test_checkout_can_expire_or_cancel_before_terminal_payment(customer):
    expires = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Expires",
        "booking_candidate",
        "expires-001",
        "idem-expires-001",
    )
    cancels = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Cancels",
        "booking_candidate",
        "cancels-001",
        "idem-cancels-001",
    )

    assert expire_checkout_session(expires.id).status == CheckoutSession.Status.EXPIRED
    assert cancel_checkout_session(cancels.id).status == CheckoutSession.Status.CANCELLED
