import json

import pytest
from django.test import Client, override_settings

from bookings.tests.factories import create_service_resource_customer


@override_settings(PUBLIC_BOOKING_ENABLED=False)
@pytest.mark.django_db
def test_public_booking_gate_returns_503_when_closed():
    service, resource, _customer = create_service_resource_customer()
    response = Client().post(
        "/api/bookings/holds/",
        data=json.dumps(
            {
                "service_public_id": str(service.id),
                "resource_public_id": str(resource.id),
                "starts_at": "2030-06-03T09:00:00+03:00",
                "idempotency_key": "booking-closed",
                "customer": {"full_name": "A", "email": "a@example.com", "phone": "+254700330001"},
            }
        ),
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 503
    payload = response.json()
    assert payload["code"] == "public_booking_closed"
    assert response["Retry-After"] == "3600"


@override_settings(PUBLIC_BOOKING_ENABLED=False)
@pytest.mark.django_db
def test_public_booking_gate_keeps_privacy_and_health_open():
    client = Client()
    health = client.get("/api/health-check/", secure=True)
    assert health.status_code in {200, 503}
    privacy = client.get("/api/bookings/privacy/data-map/", secure=True)
    assert privacy.status_code == 200


@override_settings(PUBLIC_BOOKING_ENABLED=True)
@pytest.mark.django_db
def test_public_booking_gate_allows_holds_when_open():
    service, resource, _customer = create_service_resource_customer()
    response = Client().post(
        "/api/bookings/holds/",
        data=json.dumps(
            {
                "service_public_id": str(service.id),
                "resource_public_id": str(resource.id),
                "starts_at": "2030-06-03T09:00:00+03:00",
                "idempotency_key": "booking-open",
                "customer": {"full_name": "A", "email": "a@example.com", "phone": "+254700330001"},
            }
        ),
        content_type="application/json",
        secure=True,
    )
    assert response.status_code != 503
