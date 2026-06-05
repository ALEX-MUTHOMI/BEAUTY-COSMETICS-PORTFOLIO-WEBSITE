import pytest
from django.test import Client

from bookings.tests.test_staff_portal_helpers import staff_login


@pytest.mark.django_db
def test_staff_capacity_summary_marks_normal_full_package_and_closed_days():
    client = Client()
    staff_login(client, permissions=["view_staff_portal"])

    normal = client.get("/api/staff/bookings/schedule/?date=2030-06-03", secure=True).json()
    package = client.get("/api/staff/bookings/schedule/?date=2030-06-04", secure=True).json()
    closed = client.get("/api/staff/bookings/schedule/?date=2030-06-09", secure=True).json()

    assert normal["day_type"] == "normal"
    assert normal["capacity"]["max_clients"] == 5
    assert package["day_type"] == "full_package"
    assert package["capacity"]["max_clients"] == 3
    assert closed["day_type"] == "closed"
    assert closed["capacity"]["max_clients"] == 0
