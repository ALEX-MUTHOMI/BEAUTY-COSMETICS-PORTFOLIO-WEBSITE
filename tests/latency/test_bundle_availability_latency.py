from decimal import Decimal

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from bookings.models import Service, ServiceCategory
from bookings.services.availability import AvailabilityService
from bookings.tests.test_b6_helpers import make_resource


@pytest.mark.django_db
@pytest.mark.latency
def test_bundle_availability_fourteen_day_scan_query_count_is_bounded():
    category = ServiceCategory.objects.create(name="Latency", slug="bundle-latency")
    service = Service.objects.create(
        name="Latency Service",
        slug="bundle-latency-service",
        category="latency",
        category_ref=category,
        duration_minutes=30,
        base_price=Decimal("1000.00"),
    )
    resource = make_resource()

    with CaptureQueriesContext(connection) as captured:
        AvailabilityService.get_bundle_available_slots(
            [str(service.id)], "2030-06-03", "2030-06-16", resource_id=resource.id
        )

    assert len(captured) <= 12
