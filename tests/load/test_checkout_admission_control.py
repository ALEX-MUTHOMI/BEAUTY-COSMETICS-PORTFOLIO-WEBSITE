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
    redis_client = get_redis_client()
    for key in redis_client.scan_iter("throttle:*"):
        redis_client.delete(key)


@pytest.mark.django_db(transaction=True)
@pytest.mark.load
def test_one_thousand_stk_initiation_attempts_are_admitted_or_throttled_safely():
    customer = User.objects.create_user(email="admission@aesthetic-os.test", phone_number="+254712620003")
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Admission",
        "booking_candidate",
        "admission",
        "admission-idem",
    )
    client = APIClient()
    client.force_authenticate(user=customer)
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

    statuses = []
    for index in range(1000):
        response = client.post(
            f"/api/checkout/sessions/{session.id}/mpesa/stk/",
            {
                "phone_number": customer.phone_number,
                "idempotency_key": f"admission-stk-{index}",
            },
            format="json",
            REMOTE_ADDR="198.51.100.20",
        )
        statuses.append(response.status_code)

    assert statuses.count(status.HTTP_202_ACCEPTED) == 3
    assert statuses.count(status.HTTP_429_TOO_MANY_REQUESTS) == 997
    assert not [code for code in statuses if code >= 500]
