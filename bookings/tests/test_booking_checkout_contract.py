from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking, BookingFinancialHistory, BookingPriceSnapshot
from bookings.services.holds import BookingHoldService
from bookings.tests.factories import create_service_resource_customer
from checkout.models import CheckoutSession

NAIROBI = ZoneInfo("Africa/Nairobi")


def _contract_service():
    try:
        from bookings.services.checkout_contract import BookingCheckoutContractService
    except ImportError as exc:
        pytest.fail(f"BookingCheckoutContractService missing: {exc}")
    return BookingCheckoutContractService


def _payload():
    return {"full_name": "Grace Wanjiku", "email": "grace@example.com", "phone": "+254712345678"}


def _starts(hour=9):
    return datetime.combine(date(2026, 6, 1), time(hour, 0), tzinfo=NAIROBI)


def _held_booking(service=None, resource=None, starts_at=None, key="held-booking"):
    if not service or not resource:
        service, resource, _customer = create_service_resource_customer()
    result = BookingHoldService.create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=starts_at or _starts(),
        customer_payload=_payload(),
        idempotency_key=key,
    )
    return Booking.objects.get(public_id=result["booking_public_id"])


@pytest.mark.django_db
def test_held_booking_creates_checkout_with_server_calculated_amount_and_payment_pending_state():
    booking = _held_booking()
    booking.service.base_price = Decimal("3100.00")
    booking.service.save(update_fields=["base_price", "updated_at"])

    result = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="booking-checkout-1",
        request_context={"request_id": "req-redacted", "client_amount": "0.00"},
    )

    booking.refresh_from_db()
    session = CheckoutSession.objects.get(id=booking.checkout_session_id)
    assert result["booking_public_id"] == str(booking.public_id)
    assert result["checkout_public_id"] == str(session.id)
    assert result["booking_status"] == Booking.Status.PAYMENT_PENDING
    assert result["payment_status"] == CheckoutSession.Status.PAYMENT_PENDING
    assert result["amount"] == "3100.00"
    assert result["currency"] == "KES"
    assert result["next_action"] == "initiate_payment"
    assert session.purchasable_type == "booking"
    assert session.purchasable_id == str(booking.id)
    assert session.amount_snapshot == Decimal("3100.00")
    assert booking.status == Booking.Status.PAYMENT_PENDING
    assert BookingPriceSnapshot.objects.filter(booking=booking, total_amount=Decimal("3100.00")).exists()
    assert BookingFinancialHistory.objects.filter(booking=booking, event_type="checkout_created").exists()
    assert "grace@example.com" not in str(result)
    assert "+254" not in str(result)


@pytest.mark.django_db
def test_expired_hold_cannot_create_checkout_and_does_not_reveal_booking_state():
    booking = _held_booking(key="expired-checkout")
    booking.status = Booking.Status.EXPIRED
    booking.hold_expires_at = timezone.now() - timedelta(minutes=1)
    booking.save(update_fields=["status", "hold_expires_at", "updated_at"])

    with pytest.raises(ValidationError) as exc:
        _contract_service().create_checkout_for_held_booking(
            booking_public_id=booking.public_id,
            idempotency_key="expired-checkout-key",
        )

    assert "available for checkout" in str(exc.value).lower()
    assert str(booking.id) not in str(exc.value)
    assert CheckoutSession.objects.count() == 0
