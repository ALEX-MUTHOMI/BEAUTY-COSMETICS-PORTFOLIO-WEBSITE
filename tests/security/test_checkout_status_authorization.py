from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from checkout.services import create_checkout_session

User = get_user_model()


@pytest.mark.django_db
def test_attacker_cannot_poll_another_users_checkout_status():
    owner = User.objects.create_user(email="status-owner@aesthetic-os.test", phone_number="+254712740001")
    attacker = User.objects.create_user(email="status-attacker@aesthetic-os.test", phone_number="+254712740002")
    session = create_checkout_session(
        owner,
        Decimal("160.00"),
        "KES",
        "Private status",
        "booking_candidate",
        "private-status",
        "private-status-session",
    )

    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    client.force_authenticate(user=attacker)
    response = client.get(f"/api/checkout/sessions/{session.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert str(session.id) not in str(response.data)
