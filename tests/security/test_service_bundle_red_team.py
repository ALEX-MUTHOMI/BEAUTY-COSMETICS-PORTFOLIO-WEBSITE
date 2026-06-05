from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from bookings.models import Service, ServiceCategory
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_monday, make_customer_payload, make_resource


@pytest.mark.django_db
def test_service_bundle_red_team_rejects_duplicate_inactive_and_price_tampering():
    category = ServiceCategory.objects.create(name="Red", slug="red-bundle")
    service = Service.objects.create(
        name="<script>alert(1)</script>",
        slug="red-service",
        category="red",
        category_ref=category,
        duration_minutes=30,
        base_price=Decimal("1500.00"),
    )
    inactive = Service.objects.create(
        name="Inactive",
        slug="red-inactive",
        category="red",
        category_ref=category,
        duration_minutes=30,
        base_price=Decimal("1.00"),
        is_active=False,
    )
    resource = make_resource()

    with pytest.raises(ValidationError):
        BookingHoldService.create_bundle_hold(
            service_public_ids=[str(service.id), str(service.id)],
            resource_public_id=resource.id,
            starts_at=future_monday(),
            customer_payload=make_customer_payload(),
            idempotency_key="red-duplicate",
        )
    with pytest.raises(ValidationError):
        BookingHoldService.create_bundle_hold(
            service_public_ids=[str(inactive.id)],
            resource_public_id=resource.id,
            starts_at=future_monday(),
            customer_payload=make_customer_payload(),
            idempotency_key="red-inactive",
        )
