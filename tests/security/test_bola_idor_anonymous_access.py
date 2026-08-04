from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework import status
from rest_framework.test import APIClient

from bookings.tests.factories import create_booking
from checkout.services import create_checkout_session

User = get_user_model()


def _render(response):
    if hasattr(response, "data"):
        return str(response.data)
    return response.content.decode("utf-8", errors="replace")


def _assert_no_sensitive_denial(response):
    body = _render(response)
    for marker in (
        "Traceback",
        "Internal Server Error",
        "checkout_request_id",
        "ledger_id",
        "storage_key",
        "private_bucket",
        "grace@example.com",
        "+254712345678",
    ):
        assert marker not in body


@pytest.mark.django_db
def test_anonymous_actor_cannot_access_protected_checkout_or_staff_objects():
    owner = User.objects.create_user(email="anon-owner@example.com", phone_number="+254700220001")
    session = create_checkout_session(
        owner,
        Decimal("300.00"),
        "KES",
        "Anonymous protected object",
        "booking",
        "protected-object",
        "phase-3b-anon-checkout",
    )
    booking = create_booking()

    api = APIClient()
    checkout = api.get(f"/api/checkout/sessions/{session.id}/", secure=True)
    staff_detail = Client().get(f"/api/staff/bookings/{booking.public_id}/", secure=True)
    staff_contact = Client().post(f"/api/staff/bookings/{booking.public_id}/contact-access/", secure=True)
    staff_gallery = Client().get("/api/staff/gallery/categories/", secure=True)

    assert checkout.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}
    assert staff_detail.status_code == 403
    assert staff_contact.status_code == 403
    assert staff_gallery.status_code == 403
    for response in (checkout, staff_detail, staff_contact, staff_gallery):
        _assert_no_sensitive_denial(response)


@pytest.mark.django_db
def test_public_routes_remain_public_but_do_not_expose_private_operational_fields():
    client = Client()

    for path in (
        "/health/",
        "/api/health-check/",
        "/api/bookings/catalog/services/",
        "/api/bookings/catalog/packages/",
        "/api/gallery/public/homepage/",
    ):
        response = client.get(path, secure=True)
        assert response.status_code == 200
        body = response.content.decode("utf-8", errors="replace").lower()
        for marker in ("storage_key", "private_bucket", "ledger_id", "checkout_request_id", "raw_payload"):
            assert marker not in body
