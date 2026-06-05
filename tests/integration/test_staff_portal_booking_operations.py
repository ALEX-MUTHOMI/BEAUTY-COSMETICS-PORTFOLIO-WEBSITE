import pytest
from django.test import Client

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking
from bookings.tests.test_staff_portal_helpers import staff_booking_url, staff_login, staff_payment_url


@pytest.mark.django_db(transaction=True)
def test_staff_portal_booking_detail_and_payment_summary_bridge_to_confirmed_booking(settings, tmp_path):
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("staff-portal-bridge")

    client = Client()
    staff_login(client, permissions=["view_staff_booking", "view_staff_payment_summary"])

    detail = client.get(staff_booking_url(booking), secure=True).json()
    payment = client.get(staff_payment_url(booking), secure=True).json()

    assert detail["booking_status"] == "confirmed"
    assert payment["ledger_status"] == "success"
    assert payment["refund_action_available"] is False
