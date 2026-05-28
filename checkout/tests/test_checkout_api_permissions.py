from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from checkout.services import create_checkout_session

User = get_user_model()


def secure_client():
    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    return client


@pytest.mark.django_db
def test_unauthenticated_checkout_creation_rejected():
    response = secure_client().post("/api/checkout/sessions/", {}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_can_only_access_own_checkout():
    owner = User.objects.create_user(email="owner@beauty.com", phone_number="+254712200007")
    attacker = User.objects.create_user(email="attacker@beauty.com", phone_number="+254712200008")
    session = create_checkout_session(
        owner,
        Decimal("1000.00"),
        "KES",
        "Private",
        "booking_candidate",
        "private-001",
        "private-idem-001",
    )
    client = secure_client()
    client.force_authenticate(user=attacker)

    response = client.get(f"/api/checkout/sessions/{session.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_missing_idempotency_key_rejected_for_checkout_creation():
    customer = User.objects.create_user(email="missing-idem@beauty.com", phone_number="+254712200009")
    client = secure_client()
    client.force_authenticate(user=customer)

    response = client.post(
        "/api/checkout/sessions/",
        {
            "amount": "1000.00",
            "currency": "KES",
            "description": "Missing idempotency",
            "purchasable_type": "booking_candidate",
            "purchasable_id": "missing-idem-001",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
