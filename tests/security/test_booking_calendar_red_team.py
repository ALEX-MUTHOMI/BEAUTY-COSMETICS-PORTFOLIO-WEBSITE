import uuid

import pytest
from django.test import Client

from bookings.models import FullPackage
from bookings.tests.factories import create_service_resource_customer

GENERIC_UNAVAILABLE = "Selection unavailable."
GENERIC_CALENDAR = "Calendar unavailable."


@pytest.mark.django_db
def test_calendar_api_rejects_oversized_range(client=None):
    client = Client()
    service, _resource, _customer = create_service_resource_customer()
    response = client.get(
        "/api/bookings/calendar/",
        {
            "selection_type": "normal",
            "service_public_id": str(service.id),
            "start_date": "2030-01-01",
            "end_date": "2030-03-15",
        },
        secure=True,
    )
    assert response.status_code == 400
    assert "2030-03-15" not in response.content.decode()


@pytest.mark.django_db
def test_resolve_handoff_api_rejects_path_traversal():
    response = Client().get(
        "/api/bookings/catalog/resolve-handoff/",
        {"type": "package", "plan": "..%2F..%2Fetc%2Fpasswd"},
        secure=True,
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_catalog_resolve_rejects_random_uuid_probe():
    response = Client().get(
        "/api/bookings/catalog/resolve/",
        {"selection_type": "normal", "slug": str(uuid.uuid4())},
        secure=True,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GENERIC_UNAVAILABLE


@pytest.mark.django_db
def test_calendar_rejects_random_service_uuid():
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "normal",
            "service_public_id": str(uuid.uuid4()),
        },
        secure=True,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GENERIC_CALENDAR


@pytest.mark.django_db
def test_calendar_rejects_malformed_service_uuid():
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "normal",
            "service_public_id": "not-a-valid-uuid",
        },
        secure=True,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GENERIC_CALENDAR


@pytest.mark.django_db
def test_catalog_resolve_rejects_inactive_service():
    service, _resource, _customer = create_service_resource_customer()
    service.is_active = False
    service.slug = "inactive-red-team-slug"
    service.save(update_fields=["is_active", "slug", "updated_at"])

    response = Client().get(
        "/api/bookings/catalog/resolve/",
        {"selection_type": "normal", "slug": "inactive-red-team-slug"},
        secure=True,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GENERIC_UNAVAILABLE


@pytest.mark.django_db
def test_catalog_resolve_rejects_inactive_package():
    package = FullPackage.objects.create(
        name="Inactive Package",
        slug="inactive-package-red-team",
        duration_minutes=120,
        price_amount="5000.00",
        is_active=False,
    )
    response = Client().get(
        "/api/bookings/catalog/resolve/",
        {"selection_type": "full_package", "slug": package.slug},
        secure=True,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GENERIC_UNAVAILABLE


@pytest.mark.django_db
def test_handoff_rejects_category_treatment_mismatch():
    service, _resource, _customer = create_service_resource_customer()
    service.slug = "wax-only-treatment"
    service.name = "Brow wax"
    service.category = "waxing"
    service.save(update_fields=["slug", "name", "category", "updated_at"])

    response = Client().get(
        "/api/bookings/catalog/resolve-handoff/",
        {
            "type": "single",
            "category": "facials",
            "treatment": "wax-only-treatment",
        },
        secure=True,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GENERIC_UNAVAILABLE


@pytest.mark.django_db
def test_resolve_api_does_not_leak_policy_profile():
    service, _resource, _customer = create_service_resource_customer()
    service.slug = "resolve-allowlist-test"
    service.save(update_fields=["slug", "updated_at"])
    response = Client().get(
        "/api/bookings/catalog/resolve/",
        {"selection_type": "normal", "slug": service.slug},
        secure=True,
    )
    assert response.status_code == 200
    selection = response.json()["selection"]
    assert "policy_profile" not in selection
    assert set(selection.keys()) == {
        "selection_type",
        "public_id",
        "slug",
        "name",
        "duration_minutes",
    }


@pytest.mark.django_db
def test_calendar_rejects_selection_type_tampering_package_id_as_service():
    package = FullPackage.objects.create(
        name="Tamper Package",
        slug="tamper-package-red-team",
        duration_minutes=120,
        price_amount="5000.00",
        is_active=True,
    )
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "normal",
            "service_public_id": str(package.public_id),
        },
        secure=True,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GENERIC_CALENDAR


@pytest.mark.django_db
def test_calendar_rejects_selection_type_tampering_service_id_as_package():
    service, _resource, _customer = create_service_resource_customer()
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "full_package",
            "full_package_public_id": str(service.id),
        },
        secure=True,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GENERIC_CALENDAR


@pytest.mark.django_db
def test_calendar_response_allowlist_no_price_fields():
    service, _resource, _customer = create_service_resource_customer()
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "normal",
            "service_public_id": str(service.id),
        },
        secure=True,
    )
    assert response.status_code == 200
    body = response.json()["calendar"]
    serialized = str(body).lower()
    for forbidden in ("base_price", "price_amount", "amount", "hold_id", "customer"):
        assert forbidden not in serialized
