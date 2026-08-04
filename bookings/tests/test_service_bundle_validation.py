from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from bookings.models import Service, ServiceCategory
from bookings.services.bundles import validate_service_bundle


def _service(category, slug, price="1000.00", duration=30):
    return Service.objects.create(
        name=slug.replace("-", " ").title(),
        slug=slug,
        category=category.slug,
        category_ref=category,
        duration_minutes=duration,
        base_price=Decimal(price),
    )


@pytest.mark.django_db
def test_normal_bundle_rules_are_server_authoritative_and_bounded():
    hair = ServiceCategory.objects.create(name="Hair", slug="hair")
    nails = ServiceCategory.objects.create(name="Nails", slug="nails")
    makeup = ServiceCategory.objects.create(name="Makeup", slug="makeup")
    services = [_service(hair, "hair-a"), _service(nails, "nails-a"), _service(makeup, "makeup-a")]

    summary = validate_service_bundle([str(service.id) for service in services], client_amount="1.00")

    assert summary.total_price == Decimal("3000.00")
    assert summary.total_duration_minutes == 90
    assert summary.currency == "KES"
    assert len(summary.items) == 3


@pytest.mark.django_db
def test_bundle_rejects_too_many_categories_duplicates_and_tampering_generically():
    categories = [ServiceCategory.objects.create(name=f"Cat {i}", slug=f"cat-{i}") for i in range(4)]
    services = [_service(category, f"svc-{index}") for index, category in enumerate(categories)]

    with pytest.raises(ValidationError, match="Booking selection unavailable"):
        validate_service_bundle([str(service.id) for service in services])

    with pytest.raises(ValidationError, match="Booking selection unavailable"):
        validate_service_bundle([str(services[0].id), str(services[0].id)])
