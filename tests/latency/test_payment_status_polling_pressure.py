from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from checkout.services import create_checkout_session

User = get_user_model()


@pytest.mark.django_db
def test_status_polling_pressure_is_customer_scoped_and_stable():
    owner = User.objects.create_user(email="poll-owner@beauty.com", phone_number="+254712780001")
    attacker = User.objects.create_user(email="poll-attacker@beauty.com", phone_number="+254712780002")
    session = create_checkout_session(
        owner,
        Decimal("100.00"),
        "KES",
        "Polling pressure",
        "booking_candidate",
        "polling-pressure",
        "polling-pressure-session",
    )

    owner_client = APIClient()
    owner_client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    owner_client.force_authenticate(user=owner)
    attacker_client = APIClient()
    attacker_client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    attacker_client.force_authenticate(user=attacker)

    owner_statuses = [owner_client.get(f"/api/checkout/sessions/{session.id}/").status_code for _ in range(1000)]
    attacker_status = attacker_client.get(f"/api/checkout/sessions/{session.id}/")

    assert set(owner_statuses) == {status.HTTP_200_OK}
    assert attacker_status.status_code == status.HTTP_404_NOT_FOUND
    assert str(session.id) not in str(attacker_status.data)
