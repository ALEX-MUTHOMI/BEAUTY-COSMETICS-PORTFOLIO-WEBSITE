from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from checkout.services import create_checkout_session
from users.services import get_redis_client

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_stk_push_endpoint_throttles_burst_attempts():
    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    customer = User.objects.create_user(
        email="throttle-checkout@beauty.com", phone_number="+254712200010"
    )
    session = create_checkout_session(
        customer,
        Decimal("1000.00"),
        "KES",
        "Throttle",
        "booking_candidate",
        "throttle-001",
        "throttle-idem-001",
    )
    client.force_authenticate(user=customer)
    redis_client = get_redis_client()
    for key in redis_client.scan_iter("throttle:*"):
        redis_client.delete(key)

    statuses = []
    for index in range(4):
        response = client.post(
            f"/api/checkout/sessions/{session.id}/mpesa/stk/",
            {
                "phone_number": "+254712200010",
                "idempotency_key": f"stk-throttle-{index}",
            },
            format="json",
            REMOTE_ADDR="198.51.100.20",
        )
        statuses.append(response.status_code)

    assert statuses[:3] == [status.HTTP_202_ACCEPTED] * 3
    assert statuses[3] == status.HTTP_429_TOO_MANY_REQUESTS
