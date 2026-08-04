import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device


@pytest.mark.django_db
@pytest.mark.latency
def test_remembered_device_lookup_endpoint_is_query_bounded(client):
    booking = confirmed_booking(key="remember-latency")
    remember_device(client, booking)

    with CaptureQueriesContext(connection) as captured:
        response = client.get("/api/customers/remembered-device/", secure=True)

    assert response.status_code == 200
    assert response.json()["remembered"] is True
    assert len(captured) <= 3
