from decimal import Decimal

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from bookings.models import Service, ServiceCategory
from bookings.services.availability import AvailabilityService
from bookings.tests.test_b6_helpers import make_resource


@pytest.mark.django_db
def test_bundle_availability_excludes_full_package_days_and_is_query_bounded():
    category = ServiceCategory.objects.create(name="Hair", slug="hair-availability")
    service = Service.objects.create(
        name="Hair Styling",
        slug="hair-styling-bundle",
        category="hair",
        category_ref=category,
        duration_minutes=60,
        base_price=Decimal("2500.00"),
    )
    resource = make_resource()

    with CaptureQueriesContext(connection) as captured:
        days = AvailabilityService.get_bundle_available_slots(
            [str(service.id)],
            start_date="2030-06-03",
            end_date="2030-06-06",
            resource_id=resource.id,
        )

    assert days[0]["slots"]
    assert days[1]["slots"] == []
    assert len(captured) <= 12
