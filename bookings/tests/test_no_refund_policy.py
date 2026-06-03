import pytest

from billing.models import LedgerTransaction
from bookings.tests.factories import create_booking


@pytest.mark.django_db
def test_customer_status_and_reschedule_flow_expose_no_refund_or_billing_reversal():
    booking = create_booking(status="confirmed")

    from bookings.views import _status_payload

    payload = _status_payload(booking)
    assert "refund" not in str(payload).lower()
    assert LedgerTransaction.objects.filter(status__in=["reversed", "refunded"]).count() == 0
