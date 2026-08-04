from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from bookings.models import FullPackage
from bookings.services.day_policy import validate_day_policy_for_selection
from bookings.tests.test_b6_helpers import future_monday, future_tuesday


@pytest.mark.django_db
def test_full_package_days_are_tuesday_and_wednesday_only_by_default():
    package = FullPackage.objects.create(
        name="Full Glam",
        slug="full-glam-day",
        duration_minutes=360,
        price_amount=Decimal("12000.00"),
    )

    validate_day_policy_for_selection(selection_type="full_package", starts_at=future_tuesday(), package=package)
    with pytest.raises(ValidationError):
        validate_day_policy_for_selection(selection_type="normal", starts_at=future_tuesday())
    with pytest.raises(ValidationError):
        validate_day_policy_for_selection(selection_type="full_package", starts_at=future_monday(), package=package)
