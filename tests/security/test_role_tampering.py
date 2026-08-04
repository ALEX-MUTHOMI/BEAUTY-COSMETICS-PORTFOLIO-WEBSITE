from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient

from checkout.services import create_checkout_session

User = get_user_model()


@pytest.mark.django_db
def test_role_headers_and_query_params_do_not_widen_staff_portal_authorization():
    customer = User.objects.create_user(email="role-tamper@example.com", phone_number="+254700440001")
    client = Client()
    client.force_login(customer)

    response = client.get(
        "/api/staff/bookings/schedule/?date=2026-06-08&role=admin&is_staff=true&scope=all",
        secure=True,
        HTTP_X_ROLE="admin",
        HTTP_X_ADMIN="true",
        HTTP_X_FORWARDED_USER="admin",
        HTTP_X_STAFF_ID="1",
    )

    assert response.status_code == 403
    body = response.content.decode("utf-8", errors="replace")
    assert "appointments" not in body
    assert "capacity" not in body
    assert "Traceback" not in body


@pytest.mark.django_db
def test_untrusted_identity_headers_do_not_change_checkout_object_owner():
    owner = User.objects.create_user(email="header-owner@example.com", phone_number="+254700440002")
    attacker = User.objects.create_user(email="header-attacker@example.com", phone_number="+254700440003")
    session = create_checkout_session(
        owner,
        Decimal("111.00"),
        "KES",
        "Header tamper checkout",
        "booking",
        "header-target",
        "phase-3b-header-owner",
    )
    client = APIClient()
    client.force_authenticate(user=attacker)

    response = client.get(
        f"/api/checkout/sessions/{session.id}/",
        secure=True,
        HTTP_X_USER_ID=str(owner.id),
        HTTP_X_ROLE="admin",
        HTTP_X_FORWARDED_USER=owner.email,
    )

    assert response.status_code == 404
    rendered = str(response.data)
    assert str(session.id) not in rendered
    assert "111.00" not in rendered
    assert owner.email not in rendered
