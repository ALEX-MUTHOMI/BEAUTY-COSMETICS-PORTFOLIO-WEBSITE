import pytest
from django.test import Client

from bookings.models import Booking
from bookings.tests.test_staff_portal_helpers import staff_login


@pytest.mark.django_db
def test_one_thousand_staff_schedule_requests_are_read_only_and_bounded():
    client = Client()
    staff_login(client, permissions=["view_staff_portal"])
    before = Booking.objects.count()

    for _ in range(1000):
        response = client.get("/api/staff/bookings/schedule/?date=2030-06-03", secure=True)
        assert response.status_code == 200
        assert len(response.content) < 25000

    assert Booking.objects.count() == before
