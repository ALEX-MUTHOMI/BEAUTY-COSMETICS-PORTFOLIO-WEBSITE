import pytest
from django.test import Client

from bookings.models import StaffActionAuditEvent
from bookings.tests.factories import create_booking
from bookings.tests.test_staff_portal_helpers import staff_contact_url, staff_login


@pytest.mark.django_db
def test_contact_access_requires_permission_creates_redacted_audit_and_no_store():
    booking = create_booking()

    denied = Client()
    staff_login(denied)
    assert denied.post(staff_contact_url(booking), {"reason": "call client"}, secure=True).status_code == 403

    permitted = Client()
    staff = staff_login(permitted, permissions=["view_staff_contact_details"])
    response = permitted.post(staff_contact_url(booking), {"reason": "call client"}, secure=True)
    payload = response.json()

    assert response.status_code == 200
    assert response["Cache-Control"] == "no-store"
    assert payload["phone"].startswith("+254")
    audit = StaffActionAuditEvent.objects.get(staff=staff, booking=booking)
    assert audit.action == StaffActionAuditEvent.Action.CONTACT_REVEAL
    assert "+254" not in str(audit.metadata_redacted)
    assert "grace@example.com" not in str(audit.metadata_redacted).lower()
