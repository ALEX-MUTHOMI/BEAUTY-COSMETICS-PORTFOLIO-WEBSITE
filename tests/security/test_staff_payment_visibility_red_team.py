import pytest
from django.test import Client

from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking
from bookings.tests.test_staff_portal_helpers import staff_login, staff_payment_url


@pytest.mark.django_db(transaction=True)
def test_staff_payment_visibility_red_team_exposes_no_raw_financial_identifiers(settings, tmp_path):
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, ledger = _confirm_paid_booking("staff-payment-red-team")
    client = Client()
    staff_login(client, permissions=["view_staff_payment_summary"])

    booking.refresh_from_db()
    body = client.get(staff_payment_url(booking), secure=True).content.decode()

    assert str(ledger.id) not in body
    assert booking.checkout_session_id not in body
    assert "raw_payload" not in body
    assert "refund" in body
