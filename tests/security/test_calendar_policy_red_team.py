"""Security tests for Phase 3b calendar policy + selection resolution."""

from decimal import Decimal

import pytest
from django.test import Client

from bookings.domain.selection import BookableSelection
from bookings.models import FullPackage
from bookings.services.calendar_selection import resolve_calendar_selection
from bookings.tests.factories import create_service_resource_customer

GENERIC_UNAVAILABLE = "Calendar unavailable."


@pytest.mark.django_db
def test_calendar_rejects_dual_public_ids():
    service, _resource, _customer = create_service_resource_customer()
    package = FullPackage.objects.create(
        name="Dual ID Package",
        slug="dual-id-package-red-team",
        duration_minutes=120,
        price_amount=Decimal("5000.00"),
        is_active=True,
    )
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "normal",
            "service_public_id": str(service.id),
            "full_package_public_id": str(package.public_id),
        },
        secure=True,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GENERIC_UNAVAILABLE


@pytest.mark.django_db
def test_calendar_rejects_invalid_selection_type():
    service, _resource, _customer = create_service_resource_customer()
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "admin",
            "service_public_id": str(service.id),
        },
        secure=True,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GENERIC_UNAVAILABLE


@pytest.mark.django_db
def test_calendar_rejects_empty_selection_type_with_no_ids():
    response = Client().get(
        "/api/bookings/calendar/",
        {"selection_type": "normal"},
        secure=True,
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_resolve_calendar_selection_rejects_type_id_mismatch():
    service, _resource, _customer = create_service_resource_customer()
    with pytest.raises(Exception) as exc:
        resolve_calendar_selection(
            selection_type="full_package",
            full_package_public_id=str(service.id),
        )
    assert "unavailable" in str(exc.value).lower()


@pytest.mark.django_db
def test_calendar_response_does_not_leak_business_hours():
    service, _resource, _customer = create_service_resource_customer()
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "normal",
            "service_public_id": str(service.id),
        },
        secure=True,
    )
    assert response.status_code == 200
    serialized = str(response.json()).lower()
    for forbidden in ("business_start", "business_end", "07:00:00", "19:00:00", "policy_profile"):
        assert forbidden not in serialized


@pytest.mark.django_db
def test_calendar_build_for_selection_uses_policy_profile_weekdays():
    """Weekday gate follows policy_profile, not client-supplied selection_type alone."""
    from bookings.services.booking_calendar import BookingCalendarService

    service, _resource, _customer = create_service_resource_customer()
    cross_profile = BookableSelection(
        selection_type="normal",
        public_id=service.id,
        slug=service.slug,
        name=service.name,
        duration_minutes=service.duration_minutes,
        policy_profile="full_package",
    )
    payload = BookingCalendarService.build_calendar_for_selection(
        selection=cross_profile,
        start_date=None,
        end_date=None,
    )
    assert all(day["weekday"] in {1, 2} for day in payload["days"])
    assert payload["layout"] == "singles"
