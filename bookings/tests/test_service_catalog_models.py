from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from bookings.models import Service, ServiceCategory, ServiceSubcategory
from bookings.services.catalog import list_public_services


@pytest.mark.django_db
def test_service_catalog_has_active_category_subcategory_and_safe_public_output():
    category = ServiceCategory.objects.create(name="<b>Hair</b>", slug="hair", sort_order=1)
    subcategory = ServiceSubcategory.objects.create(category=category, name="Braids", slug="braids")
    service = Service.objects.create(
        name="<img src=x onerror=alert(1)> Box Braids",
        slug="box-braids",
        category="legacy-hair",
        category_ref=category,
        subcategory=subcategory,
        duration_minutes=90,
        base_price=Decimal("3500.00"),
    )

    payload = list_public_services()

    assert payload[0]["public_id"] == str(service.id)
    assert "<" not in str(payload)
    assert "onerror" not in str(payload).lower()
    assert "3500.00" in str(payload)
    assert "id" not in payload[0]


@pytest.mark.django_db
def test_inactive_service_is_rejected_for_public_selection():
    category = ServiceCategory.objects.create(name="Nails", slug="nails")
    service = Service.objects.create(
        name="Inactive manicure",
        slug="inactive-manicure",
        category="legacy-nails",
        category_ref=category,
        duration_minutes=60,
        base_price=Decimal("1000.00"),
        is_active=False,
    )

    with pytest.raises(ValidationError):
        list_public_services(service_public_ids=[str(service.id)])
