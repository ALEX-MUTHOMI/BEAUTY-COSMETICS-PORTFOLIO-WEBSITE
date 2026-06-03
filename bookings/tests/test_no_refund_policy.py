import pytest

from billing.models import LedgerTransaction
from bookings.tests.factories import create_booking


@pytest.mark.django_db
def test_customer_status_and_reschedule_flow_expose_no_refund_or_billing_reversal():
    booking = create_booking(status="confirmed")

    from bookings.views import _status_payload

    payload = _status_payload(booking)
    assert "paid bookings are non-refundable" in str(payload).lower()
    assert "rescheduling may be available according to the booking policy" in str(payload).lower()
    assert "refund_url" not in payload
    assert "refund_action" not in payload
    assert LedgerTransaction.objects.filter(status__in=["reversed", "refunded"]).count() == 0
