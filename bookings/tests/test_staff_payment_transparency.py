import pytest
from django.test import Client

from bookings.models import Booking
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking
from bookings.tests.test_staff_portal_helpers import staff_booking_url, staff_login, staff_payment_url


@pytest.mark.django_db(transaction=True)
def test_payment_transparency_is_permission_gated_redacted_and_read_only(settings, tmp_path):
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("staff-payment-transparency")

    no_payment = Client()
    staff_login(no_payment, permissions=["view_staff_booking"])
    detail = no_payment.get(staff_booking_url(booking), secure=True).json()
    assert "payment_summary" not in detail
    assert no_payment.get(staff_payment_url(booking), secure=True).status_code == 403

    permitted = Client()
    staff_login(permitted, permissions=["view_staff_booking", "view_staff_payment_summary"])
    response = permitted.get(staff_payment_url(booking), secure=True)
    payload = response.json()

    booking.refresh_from_db()
    assert response.status_code == 200
    assert payload["payment_status"] == "paid"
    assert payload["amount"]
    assert payload["currency"] == "KES"
    assert payload["ledger_status"] == "success"
    assert payload["refund_action_available"] is False
    assert booking.status == Booking.Status.CONFIRMED
    body = str(payload)
    assert booking.checkout_session_id not in body
    assert str(_ledger.id) not in body
    assert "raw_payload" not in body
