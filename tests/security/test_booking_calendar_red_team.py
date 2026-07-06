import pytest
from django.test import Client


@pytest.mark.django_db
def test_calendar_api_rejects_oversized_range(client=None):
    client = Client()
    from bookings.tests.factories import create_service_resource_customer

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
