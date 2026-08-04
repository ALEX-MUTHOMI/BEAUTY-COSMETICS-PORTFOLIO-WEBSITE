import pytest

from bookings.models import BookingFinancialHistory
from bookings.tests.factories import create_booking


@pytest.mark.django_db
def test_booking_financial_history_is_operational_and_does_not_import_billing_services():
    booking = create_booking()
    history = BookingFinancialHistory.objects.create(
        booking=booking,
        event_type=BookingFinancialHistory.EventType.CHECKOUT_LINKED,
        checkout_session_id="checkout-id-only",
        billing_ledger_id="",
        amount="0.00",
        currency="KES",
        no_refund_policy_version="v1",
    )

    assert history.checkout_session_id == "checkout-id-only"
    assert not hasattr(history, "create_refund")
    assert not hasattr(history, "mutate_ledger")
