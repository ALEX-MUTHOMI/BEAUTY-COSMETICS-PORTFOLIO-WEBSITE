from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking, FullPackage
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_tuesday, make_customer_payload, make_resource


@pytest.mark.django_db(transaction=True)
@pytest.mark.load
def test_full_package_day_capacity_pressure_caps_at_three():
    package = FullPackage.objects.create(
        name="Package Load",
        slug="package-load",
        duration_minutes=120,
        price_amount=Decimal("8000.00"),
    )
    resource = make_resource()
    accepted = 0

    for index in range(6):
        try:
            BookingHoldService.create_full_package_hold(
                full_package_public_id=str(package.public_id),
                resource_public_id=resource.id,
                starts_at=future_tuesday() + timezone.timedelta(hours=2 * index),
                customer_payload=make_customer_payload(),
                idempotency_key=f"package-load-{index}",
            )
            accepted += 1
        except ValidationError:
            pass

    assert accepted == 3
    assert Booking.objects.filter(booking_type=Booking.BookingType.FULL_PACKAGE).count() == 3
