from decimal import Decimal

import pytest

from bookings.models import Service, ServiceCategory
from bookings.services.availability import AvailabilityService
from bookings.tests.test_b6_helpers import make_resource


@pytest.mark.django_db
@pytest.mark.load
def test_one_thousand_bundle_availability_requests_are_bounded():
    category = ServiceCategory.objects.create(name="Load", slug="bundle-load")
    service = Service.objects.create(
        name="Load Service",
        slug="bundle-load-service",
        category="load",
        category_ref=category,
        duration_minutes=30,
        base_price=Decimal("1000.00"),
    )
    resource = make_resource()

    for _ in range(1000):
        days = AvailabilityService.get_bundle_available_slots(
            [str(service.id)], "2030-06-03", "2030-06-03", resource_id=resource.id
        )

    assert days[0]["slots"]
