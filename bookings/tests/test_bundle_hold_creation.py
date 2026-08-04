from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from bookings.models import Booking, Service, ServiceCategory
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_monday, future_tuesday, make_customer_payload, make_resource


@pytest.mark.django_db
def test_normal_bundle_hold_succeeds_on_monday_and_rejects_tuesday():
    category = ServiceCategory.objects.create(name="Hair", slug="hair-hold")
    service = Service.objects.create(
        name="Styling",
        slug="styling-hold",
        category="hair",
        category_ref=category,
        duration_minutes=60,
        base_price=Decimal("2500.00"),
    )
    resource = make_resource()

    result = BookingHoldService.create_bundle_hold(
        service_public_ids=[str(service.id)],
        resource_public_id=resource.id,
        starts_at=future_monday(),
        customer_payload=make_customer_payload(),
        idempotency_key="bundle-hold-monday",
    )

    booking = Booking.objects.get(public_id=result["booking_public_id"])
    assert booking.total_price_snapshot == Decimal("2500.00")
    assert booking.local_booking_date.isoformat() == "2030-06-03"

    with pytest.raises(ValidationError):
        BookingHoldService.create_bundle_hold(
            service_public_ids=[str(service.id)],
            resource_public_id=resource.id,
            starts_at=future_tuesday(),
            customer_payload=make_customer_payload(),
            idempotency_key="bundle-hold-tuesday",
        )
