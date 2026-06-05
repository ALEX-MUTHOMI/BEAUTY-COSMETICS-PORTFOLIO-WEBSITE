from decimal import Decimal

import pytest

from bookings.models import Booking, BookingPriceSnapshot, Service, ServiceCategory
from bookings.services.checkout_contract import _booking_amount
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_monday, make_customer_payload, make_resource


@pytest.mark.django_db
def test_bundle_checkout_amount_uses_server_snapshots_not_client_amount():
    category = ServiceCategory.objects.create(name="Hair", slug="hair-checkout")
    services = [
        Service.objects.create(
            name=f"Service {index}",
            slug=f"checkout-service-{index}",
            category="hair",
            category_ref=category,
            duration_minutes=30,
            base_price=Decimal("1500.00"),
        )
        for index in range(2)
    ]
    resource = make_resource()
    result = BookingHoldService.create_bundle_hold(
        service_public_ids=[str(service.id) for service in services],
        resource_public_id=resource.id,
        starts_at=future_monday(),
        customer_payload=make_customer_payload(),
        idempotency_key="bundle-checkout",
        client_amount="1.00",
    )
    booking = Booking.objects.get(public_id=result["booking_public_id"])

    assert _booking_amount(booking)["total_amount"] == Decimal("3000.00")
    snapshot = BookingPriceSnapshot.objects.create(
        booking=booking,
        base_service_price=Decimal("3000.00"),
        total_amount=Decimal("3000.00"),
        currency="KES",
    )
    assert snapshot.total_amount == Decimal("3000.00")
