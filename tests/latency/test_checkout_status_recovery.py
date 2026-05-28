from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from checkout.services import create_checkout_session, initiate_mpesa_stk

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_mobile_reload_can_recover_checkout_status_after_stk_sent():
    customer = User.objects.create_user(
        email="status-recovery@beauty.com", phone_number="+254712730003"
    )
    session = create_checkout_session(
        customer,
        Decimal("140.00"),
        "KES",
        "Status recovery",
        "booking_candidate",
        "status-recovery",
        "status-recovery-session",
    )
    initiate_mpesa_stk(session.id, customer.phone_number, "status-recovery-stk")

    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"
    client.force_authenticate(user=customer)
    response = client.get(f"/api/checkout/sessions/{session.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "stk_sent"
    assert response.data["id"] == str(session.id)
