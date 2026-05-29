from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from checkout.services import create_checkout_session

User = get_user_model()


class BrokenRedis:
    def eval(self, *args, **kwargs):
        raise ConnectionError("redis unavailable")


@pytest.mark.django_db(transaction=True)
@pytest.mark.load
def test_redis_throttle_failure_returns_controlled_rejection(monkeypatch):
    customer = User.objects.create_user(email="redis-failure@beauty.com", phone_number="+254712620005")
    session = create_checkout_session(
        customer,
        Decimal("100.00"),
        "KES",
        "Redis failure",
        "booking_candidate",
        "redis-failure",
        "redis-failure-idem",
    )
    monkeypatch.setattr("users.services.get_redis_client", lambda: BrokenRedis())
    client = APIClient()
    client.force_authenticate(user=customer)
    client.raise_request_exception = False
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

    response = client.post(
        f"/api/checkout/sessions/{session.id}/mpesa/stk/",
        {"phone_number": customer.phone_number, "idempotency_key": "redis-failure-stk"},
        format="json",
        REMOTE_ADDR="198.51.100.21",
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
