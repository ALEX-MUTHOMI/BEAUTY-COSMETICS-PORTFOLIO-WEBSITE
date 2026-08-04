from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import FullPackage
from bookings.services.day_policy import validate_day_policy_for_selection


@pytest.mark.django_db
def test_full_package_requires_twenty_four_hour_notice_and_same_day_is_rejected():
    package = FullPackage.objects.create(
        name="Full Glam Notice",
        slug="full-glam-notice",
        duration_minutes=360,
        price_amount=Decimal("12000.00"),
    )
    now = timezone.datetime(2030, 6, 4, 8, 0, tzinfo=timezone.get_current_timezone())
    same_day = timezone.datetime(2030, 6, 4, 10, 0, tzinfo=timezone.get_current_timezone())

    with pytest.raises(ValidationError, match="Booking selection unavailable"):
        validate_day_policy_for_selection(
            selection_type="full_package",
            starts_at=same_day,
            package=package,
            now=now,
        )
