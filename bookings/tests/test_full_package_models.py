from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from bookings.models import FullPackage
from bookings.services.bundles import get_full_package_summary, list_public_full_packages


@pytest.mark.django_db
def test_full_package_is_predefined_active_and_public_safe():
    package = FullPackage.objects.create(
        name="<script>Full Glam</script>",
        slug="full-glam",
        duration_minutes=360,
        price_amount=Decimal("12000.00"),
    )

    listed = list_public_full_packages()
    summary = get_full_package_summary(str(package.public_id))

    assert listed[0]["public_id"] == str(package.public_id)
    assert summary.total_price == Decimal("12000.00")
    assert "<script>" not in str(listed)


@pytest.mark.django_db
def test_inactive_full_package_rejected_and_client_cannot_define_custom_package():
    package = FullPackage.objects.create(
        name="Inactive",
        slug="inactive",
        duration_minutes=360,
        price_amount=Decimal("12000.00"),
        is_active=False,
    )

    with pytest.raises(ValidationError):
        get_full_package_summary(str(package.public_id))

    with pytest.raises(ValidationError):
        get_full_package_summary({"name": "custom", "price": "1.00"})
