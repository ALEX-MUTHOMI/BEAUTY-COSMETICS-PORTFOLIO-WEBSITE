from decimal import Decimal

import pytest

from bookings.models import Booking, FullPackage
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_tuesday, make_customer_payload, make_resource


@pytest.mark.django_db
def test_full_package_booking_lifecycle_uses_predefined_package_snapshot():
    package = FullPackage.objects.create(
        name="Full Package Lifecycle",
        slug="full-package-lifecycle",
        duration_minutes=360,
        price_amount=Decimal("12000.00"),
    )
    result = BookingHoldService.create_full_package_hold(
        full_package_public_id=str(package.public_id),
        resource_public_id=make_resource().id,
        starts_at=future_tuesday(),
        customer_payload=make_customer_payload(),
        idempotency_key="package-lifecycle",
    )
    booking = Booking.objects.get(public_id=result["booking_public_id"])

    assert booking.booking_type == Booking.BookingType.FULL_PACKAGE
    assert booking.full_package_id == package.id
    assert booking.total_price_snapshot == Decimal("12000.00")
