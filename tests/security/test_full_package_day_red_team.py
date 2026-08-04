from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from bookings.models import FullPackage
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_monday, future_tuesday, make_customer_payload, make_resource


@pytest.mark.django_db
def test_full_package_day_red_team_rejects_wrong_day_and_client_tampering():
    package = FullPackage.objects.create(
        name="<svg/onload=alert(1)>",
        slug="red-team-package",
        duration_minutes=360,
        price_amount=Decimal("12000.00"),
    )
    resource = make_resource()

    with pytest.raises(ValidationError):
        BookingHoldService.create_full_package_hold(
            full_package_public_id=str(package.public_id),
            resource_public_id=resource.id,
            starts_at=future_monday(),
            customer_payload=make_customer_payload(),
            idempotency_key="package-red-wrong-day",
            client_amount="1.00",
        )

    result = BookingHoldService.create_full_package_hold(
        full_package_public_id=str(package.public_id),
        resource_public_id=resource.id,
        starts_at=future_tuesday(),
        customer_payload=make_customer_payload(),
        idempotency_key="package-red-valid",
        client_amount="1.00",
    )
    assert "svg" not in str(result).lower()
