import pytest
from django.test import Client

from bookings.models import StaffActionAuditEvent
from bookings.tests.factories import create_booking
from bookings.tests.test_staff_portal_helpers import staff_contact_url, staff_login


@pytest.mark.django_db
def test_staff_contact_access_red_team_requires_reason_and_rejects_csrfless_post():
    booking = create_booking()
    client = Client(enforce_csrf_checks=True)
    staff_login(client, permissions=["view_staff_contact_details"])

    assert client.post(staff_contact_url(booking), {"reason": ""}, secure=True).status_code == 403
    assert StaffActionAuditEvent.objects.count() == 0
