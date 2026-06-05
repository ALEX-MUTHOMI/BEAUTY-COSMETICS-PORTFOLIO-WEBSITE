from decimal import Decimal

import pytest

from bookings.models import Booking, Service, ServiceCategory
from bookings.services.holds import BookingHoldService
from bookings.services.receipts import _receipt_snapshot
from bookings.tests.test_b6_helpers import future_monday, make_customer_payload, make_resource


@pytest.mark.django_db
def test_bundle_receipt_snapshot_lists_selected_services_safely():
    category = ServiceCategory.objects.create(name="Hair", slug="hair-receipt")
    service = Service.objects.create(
        name="<img src=x onerror=1> Blow Dry",
        slug="receipt-blow-dry",
        category="hair",
        category_ref=category,
        duration_minutes=60,
        base_price=Decimal("2500.00"),
    )
    result = BookingHoldService.create_bundle_hold(
        service_public_ids=[str(service.id)],
        resource_public_id=make_resource().id,
        starts_at=future_monday(),
        customer_payload=make_customer_payload(),
        idempotency_key="bundle-receipt",
    )
    booking = Booking.objects.get(public_id=result["booking_public_id"])
    ledger = type("Ledger", (), {"amount": Decimal("2500.00"), "currency": "KES", "credited_at": None})()
    snapshot = _receipt_snapshot(booking, None, ledger)

    assert snapshot["selected_items"][0]["name"] == "Blow Dry"
    assert "<" not in str(snapshot)
