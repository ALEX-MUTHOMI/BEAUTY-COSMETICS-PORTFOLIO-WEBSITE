from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from checkout.services import create_checkout_session
from users.services import get_redis_client

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_throttle_keys():
    client = get_redis_client()
    for key in client.scan_iter("throttle:*"):
        client.delete(key)


@pytest.mark.django_db(transaction=True)
def test_checkout_stk_throttling_under_burst_pressure():
    customer = User.objects.create_user(email="pressure-throttle@beauty.com", phone_number="+254712600009")
    session = create_checkout_session(
        customer,
        Decimal("1000.00"),
        "KES",
        "Throttle",
        "booking_candidate",
        "pressure-throttle",
        "pressure-idem",
    )
    client = APIClient()
    client.force_authenticate(user=customer)
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

    statuses = [
        client.post(
            f"/api/checkout/sessions/{session.id}/mpesa/stk/",
            {
                "phone_number": customer.phone_number,
                "idempotency_key": f"pressure-stk-{index}",
            },
            format="json",
            REMOTE_ADDR="198.51.100.10",
        ).status_code
        for index in range(10)
    ]

    assert statuses[:3] == [status.HTTP_202_ACCEPTED] * 3
    assert statuses.count(status.HTTP_429_TOO_MANY_REQUESTS) == 7
