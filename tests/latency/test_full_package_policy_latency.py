from decimal import Decimal

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from bookings.models import FullPackage
from bookings.services.availability import AvailabilityService
from bookings.tests.test_b6_helpers import make_resource


@pytest.mark.django_db
@pytest.mark.latency
def test_full_package_policy_availability_is_query_bounded():
    package = FullPackage.objects.create(
        name="Latency Package",
        slug="latency-package",
        duration_minutes=240,
        price_amount=Decimal("10000.00"),
    )
    resource = make_resource()

    with CaptureQueriesContext(connection) as captured:
        days = AvailabilityService.get_full_package_available_slots(
            str(package.public_id), "2030-06-03", "2030-06-10", resource_id=resource.id
        )

    assert any(day["slots"] for day in days if day["date"] in {"2030-06-04", "2030-06-05"})
    assert len(captured) <= 12
