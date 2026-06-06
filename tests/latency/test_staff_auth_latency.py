import pytest
from django.test import Client

from bookings.tests.test_staff_auth_helpers import login_payload, make_staff


@pytest.mark.django_db
def test_staff_me_endpoint_is_bounded_for_repeated_status_checks():
    make_staff()
    client = Client()
    assert (
        client.post(
            "/api/staff/auth/login/",
            login_payload(),
            content_type="application/json",
            secure=True,
        ).status_code
        == 200
    )

    statuses = [client.get("/api/staff/auth/me/", secure=True).status_code for _ in range(50)]

    assert statuses == [200] * 50
