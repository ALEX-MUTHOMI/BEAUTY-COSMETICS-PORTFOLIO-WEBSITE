import pytest
from decimal import Decimal

from bookings.services.handoff_resolve import resolve_booking_handoff
from bookings.models import FullPackage, Service


@pytest.mark.django_db
def test_handoff_resolve_package_plan_slug():
    package = FullPackage.objects.create(
        name="Classic Full Package",
        slug="classic-full-package",
        duration_minutes=240,
        price_amount=Decimal("12000.00"),
    )
    resolved = resolve_booking_handoff(handoff_type="package", plan_slug="classic-full-package")
    assert resolved["public_id"] == str(package.public_id)


@pytest.mark.django_db
def test_handoff_resolve_single_treatment_slug():
    service = Service.objects.create(
        name="Brow shaping",
        slug="brow-shaping",
        category="waxing",
        duration_minutes=20,
        base_price=Decimal("800.00"),
    )
    resolved = resolve_booking_handoff(
        handoff_type="single",
        category_slug="waxing",
        treatment_slug="brow-shaping",
    )
    assert resolved["public_id"] == str(service.id)


@pytest.mark.django_db
def test_handoff_resolve_rejects_injection():
    with pytest.raises(Exception):
        resolve_booking_handoff(handoff_type="single", category_slug="<script>", treatment_slug="x")
