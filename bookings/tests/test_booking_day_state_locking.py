from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking, BookingDayState, Service, ServiceCategory
from bookings.services.holds import BookingHoldService
from bookings.tests.test_b6_helpers import future_monday, make_customer_payload, make_resource


@pytest.mark.django_db(transaction=True)
def test_day_state_lock_prevents_normal_day_capacity_above_five():
    category = ServiceCategory.objects.create(name="Hair", slug="hair-lock")
    service = Service.objects.create(
        name="Quick hair",
        slug="quick-hair-lock",
        category="hair",
        category_ref=category,
        duration_minutes=30,
        base_price=Decimal("1000.00"),
    )
    resource = make_resource()

    for index in range(5):
        BookingHoldService.create_bundle_hold(
            service_public_ids=[str(service.id)],
            resource_public_id=resource.id,
            starts_at=future_monday() + timezone.timedelta(minutes=60 * index),
            customer_payload=make_customer_payload(),
            idempotency_key=f"normal-cap-{index}",
        )

    with pytest.raises(ValidationError):
        BookingHoldService.create_bundle_hold(
            service_public_ids=[str(service.id)],
            resource_public_id=resource.id,
            starts_at=future_monday() + timezone.timedelta(hours=6),
            customer_payload=make_customer_payload(),
            idempotency_key="normal-cap-over",
        )

    assert Booking.objects.filter(status=Booking.Status.HELD).count() == 5
    assert BookingDayState.objects.get(local_date=future_monday().astimezone(timezone.get_fixed_timezone(180)).date())
