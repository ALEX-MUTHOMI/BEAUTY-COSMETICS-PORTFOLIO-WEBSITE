import pytest

from bookings.models import BookingFinancialHistory, BookingPriceSnapshot
from bookings.tests.test_booking_checkout_contract import _contract_service, _held_booking


@pytest.mark.django_db
def test_checkout_contract_creates_operational_financial_history_without_raw_provider_ids():
    booking = _held_booking(key="financial-history-hold")

    result = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="financial-history-checkout",
    )

    snapshot = BookingPriceSnapshot.objects.get(booking=booking)
    histories = list(BookingFinancialHistory.objects.filter(booking=booking).order_by("created_at"))
    assert snapshot.total_amount == snapshot.base_service_price
    assert [history.event_type for history in histories] == ["checkout_created", "payment_pending"]
    assert all(history.amount == snapshot.total_amount for history in histories)
    assert all(history.currency == "KES" for history in histories)
    assert all("ws_CO" not in history.provider_reference_hash for history in histories)
    assert "provider" not in str(result).lower()
