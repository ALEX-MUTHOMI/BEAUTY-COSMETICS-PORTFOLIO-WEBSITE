from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from checkout.models import CheckoutSession
from checkout.services import create_checkout_session

User = get_user_model()


@pytest.mark.django_db(transaction=True)
@pytest.mark.load
def test_one_thousand_checkout_session_creation_attempts_do_not_crash():
    customer = User.objects.create_user(email="load-checkout@aesthetic-os.test", phone_number="+254712620001")

    statuses = [
        create_checkout_session(
            customer,
            Decimal("100.00"),
            "KES",
            "Load checkout",
            "booking_candidate",
            f"load-checkout-{index}",
            f"load-checkout-idem-{index}",
        ).status
        for index in range(1000)
    ]

    assert statuses.count(CheckoutSession.Status.CREATED) == 1000
    assert CheckoutSession.objects.count() == 1000
