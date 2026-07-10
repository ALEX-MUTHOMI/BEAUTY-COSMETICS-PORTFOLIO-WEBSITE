from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from checkout.services import create_checkout_session

User = get_user_model()


@pytest.mark.django_db
def test_owner_stk_endpoint_rejects_anonymous_guests():
    """Guests must use /api/bookings/checkout/mpesa/stk/ — owner STK stays IsAuthenticated."""
    customer = User.objects.create_user(email="owner-stk@aesthetic-os.test", phone_number="+254712200099")
    session = create_checkout_session(
        customer,
        Decimal("1500.00"),
        "KES",
        "Owner STK auth wall",
        "booking_candidate",
        "owner-stk-auth-001",
        "owner-stk-auth-idem-001",
    )
    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    response = client.post(
        f"/api/checkout/sessions/{session.id}/mpesa/stk/",
        {
            "phone_number": "+254712200099",
            "idempotency_key": "owner-stk-anon-1",
        },
        format="json",
    )
    assert response.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}
