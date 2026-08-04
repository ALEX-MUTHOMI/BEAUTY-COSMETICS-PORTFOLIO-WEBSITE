from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking, Service, ServiceCategory
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_monday, make_customer_payload, make_resource


@pytest.mark.django_db(transaction=True)
def test_day_capacity_red_team_cannot_exceed_normal_cap_sequential_pressure():
    category = ServiceCategory.objects.create(name="Cap", slug="cap-red")
    service = Service.objects.create(
        name="Cap service",
        slug="cap-service-red",
        category="cap",
        category_ref=category,
        duration_minutes=30,
        base_price=Decimal("1000.00"),
    )
    resource = make_resource()

    accepted = 0
    for index in range(10):
        try:
            BookingHoldService.create_bundle_hold(
                service_public_ids=[str(service.id)],
                resource_public_id=resource.id,
                starts_at=future_monday() + timezone.timedelta(minutes=45 * index),
                customer_payload=make_customer_payload(),
                idempotency_key=f"cap-red-{index}",
            )
            accepted += 1
        except ValidationError:
            pass

    assert accepted == 5
    assert Booking.objects.filter(status=Booking.Status.HELD).count() == 5
