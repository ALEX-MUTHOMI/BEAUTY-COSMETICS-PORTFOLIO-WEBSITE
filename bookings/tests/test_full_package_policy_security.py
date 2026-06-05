from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from bookings.models import FullPackage
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_monday, future_tuesday, make_customer_payload, make_resource


@pytest.mark.django_db
def test_full_package_public_errors_are_generic_and_no_custom_composition_allowed():
    package = FullPackage.objects.create(
        name="Full Glam Security",
        slug="full-glam-security",
        duration_minutes=360,
        price_amount=Decimal("12000.00"),
    )
    resource = make_resource()

    with pytest.raises(ValidationError, match="Availability unavailable"):
        BookingHoldService.create_full_package_hold(
            full_package_public_id=str(package.public_id),
            resource_public_id=resource.id,
            starts_at=future_monday(),
            customer_payload=make_customer_payload(),
            idempotency_key="package-wrong-day",
            client_package_items=["custom"],
        )

    result = BookingHoldService.create_full_package_hold(
        full_package_public_id=str(package.public_id),
        resource_public_id=resource.id,
        starts_at=future_tuesday(),
        customer_payload=make_customer_payload(),
        idempotency_key="package-correct-day",
    )
    assert result["next_action"] == "checkout_required"
