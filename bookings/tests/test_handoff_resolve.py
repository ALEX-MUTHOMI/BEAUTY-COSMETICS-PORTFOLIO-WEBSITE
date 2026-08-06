from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from bookings.models import FullPackage, Service
from bookings.services.handoff_resolve import resolve_booking_handoff


@pytest.mark.django_db
def test_handoff_resolve_package_plan_slug():
    package, _created = FullPackage.objects.get_or_create(
        slug="classic-full-package",
        defaults={
            "name": "Classic Full Package",
            "duration_minutes": 240,
            "price_amount": Decimal("12000.00"),
            "is_active": True,
        },
    )
    resolved = resolve_booking_handoff(handoff_type="package", plan_slug="classic-full-package")
    assert str(resolved.public_id) == str(package.public_id)


@pytest.mark.django_db
def test_handoff_resolve_single_treatment_slug():
    service, _created = Service.objects.get_or_create(
        slug="brow-shaping",
        defaults={
            "name": "Brow shaping",
            "category": "waxing",
            "duration_minutes": 20,
            "base_price": Decimal("800.00"),
            "is_active": True,
        },
    )
    resolved = resolve_booking_handoff(
        handoff_type="single",
        category_slug="waxing",
        treatment_slug="brow-shaping",
    )
    assert str(resolved.public_id) == str(service.id)


@pytest.mark.django_db
def test_handoff_resolve_rejects_injection():
    with pytest.raises(ValidationError):
        resolve_booking_handoff(handoff_type="single", category_slug="<script>", treatment_slug="x")
