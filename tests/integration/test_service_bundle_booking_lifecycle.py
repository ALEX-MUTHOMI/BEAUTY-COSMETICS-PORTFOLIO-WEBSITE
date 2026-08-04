from decimal import Decimal

import pytest

from bookings.models import Booking, Service, ServiceCategory
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_monday, make_customer_payload, make_resource


@pytest.mark.django_db
def test_service_bundle_booking_lifecycle_creates_one_continuous_hold():
    category = ServiceCategory.objects.create(name="Lifecycle", slug="lifecycle-bundle")
    services = [
        Service.objects.create(
            name=f"Lifecycle {index}",
            slug=f"lifecycle-bundle-{index}",
            category="lifecycle",
            category_ref=category,
            duration_minutes=30,
            base_price=Decimal("1000.00"),
        )
        for index in range(2)
    ]
    result = BookingHoldService.create_bundle_hold(
        service_public_ids=[str(service.id) for service in services],
        resource_public_id=make_resource().id,
        starts_at=future_monday(),
        customer_payload=make_customer_payload(),
        idempotency_key="bundle-lifecycle",
    )
    booking = Booking.objects.get(public_id=result["booking_public_id"])

    assert booking.service_items.count() == 2
    assert booking.total_duration_minutes == 60
    assert booking.total_price_snapshot == Decimal("2000.00")
    assert booking.status == Booking.Status.HELD
