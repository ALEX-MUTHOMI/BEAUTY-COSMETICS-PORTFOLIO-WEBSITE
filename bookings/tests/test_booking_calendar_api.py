from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.test import Client
from django.utils import timezone

from bookings.domain.calendar import MAX_CALENDAR_RANGE_DAYS, STATUS_AVAILABLE, STATUS_CAPACITY_FULL, STATUS_NOT_OFFERED
from bookings.models import Booking, FullPackage, Service
from bookings.services.booking_calendar import BookingCalendarService
from bookings.services.catalog_resolve import resolve_catalog_selection
from bookings.tests.factories import create_booking, create_service_resource_customer


def _future_weekday(target):
    today = timezone.localdate()
    delta = (target - today.weekday()) % 7
    if delta == 0:
        delta = 7
    return today + timedelta(days=delta)


@pytest.mark.django_db
def test_resolve_package_slug_returns_public_id_only():
    package = FullPackage.objects.create(
        name="Classic Full Package",
        slug="classic-full-package",
        duration_minutes=240,
        price_amount=Decimal("12000.00"),
    )
    resolved = resolve_catalog_selection(selection_type="full_package", slug="classic-full-package")
    assert resolved["public_id"] == str(package.public_id)
    assert resolved["name"] == "Classic Full Package"
    assert "<" not in resolved["name"]


@pytest.mark.django_db
def test_resolve_rejects_malicious_slug():
    with pytest.raises(ValidationError):
        resolve_catalog_selection(selection_type="normal", slug="../admin")
    with pytest.raises(ValidationError):
        resolve_catalog_selection(selection_type="normal", slug="<script>")


@pytest.mark.django_db
def test_calendar_marks_tuesday_unavailable_for_normal_selection():
    service, resource, _customer = create_service_resource_customer()
    monday = _future_weekday(0)
    end = monday + timedelta(days=6)

    payload = BookingCalendarService.build_calendar(
        selection_type="normal",
        service_public_id=str(service.id),
        start_date=monday,
        end_date=end,
    )

    tuesday = monday + timedelta(days=1)
    tuesday_day = next(day for day in payload["days"] if day["date"] == tuesday.isoformat())
    assert tuesday_day["status"] == STATUS_NOT_OFFERED


@pytest.mark.django_db
def test_calendar_marks_monday_unavailable_for_package_selection():
    _service, _resource, _customer = create_service_resource_customer()
    package = FullPackage.objects.create(
        name="Glow Package",
        slug="glow-package",
        duration_minutes=180,
        price_amount=Decimal("8500.00"),
    )
    monday = _future_weekday(0)
    end = monday + timedelta(days=6)

    payload = BookingCalendarService.build_calendar(
        selection_type="full_package",
        full_package_public_id=str(package.public_id),
        start_date=monday,
        end_date=end,
    )

    monday_day = next(day for day in payload["days"] if day["date"] == monday.isoformat())
    assert monday_day["status"] == STATUS_NOT_OFFERED


@pytest.mark.django_db
def test_calendar_shows_capacity_remaining_on_available_normal_day():
    service, resource, _customer = create_service_resource_customer()
    monday = _future_weekday(0)

    payload = BookingCalendarService.build_calendar(
        selection_type="normal",
        service_public_id=str(service.id),
        start_date=monday,
        end_date=monday,
    )

    day = payload["days"][0]
    assert day["status"] == STATUS_AVAILABLE
    assert day["capacity"]["max"] == 5
    assert day["capacity"]["remaining"] == 5
    assert day["slot_count"] > 0


@pytest.mark.django_db
def test_calendar_marks_day_capacity_full_when_max_clients_reached():
    service, resource, customer = create_service_resource_customer()
    monday = _future_weekday(0)
    for hour in range(5):
        create_booking(
            service=service,
            resource=resource,
            customer_profile=customer,
            starts_at=timezone.make_aware(
                timezone.datetime.combine(monday, timezone.datetime.min.time().replace(hour=7 + hour)),
                timezone.get_current_timezone(),
            ),
            status=Booking.Status.CONFIRMED,
            local_booking_date=monday,
        )

    payload = BookingCalendarService.build_calendar(
        selection_type="normal",
        service_public_id=str(service.id),
        start_date=monday,
        end_date=monday,
    )

    assert payload["days"][0]["status"] == STATUS_CAPACITY_FULL
    assert payload["days"][0]["capacity"]["remaining"] == 0


@pytest.mark.django_db
def test_calendar_rejects_excessive_range():
    service, _resource, _customer = create_service_resource_customer()
    start = timezone.localdate()
    end = start + timedelta(days=MAX_CALENDAR_RANGE_DAYS)

    with pytest.raises(ValidationError):
        BookingCalendarService.build_calendar(
            selection_type="normal",
            service_public_id=str(service.id),
            start_date=start,
            end_date=end,
        )


@pytest.mark.django_db
def test_calendar_api_returns_safe_json_without_internal_ids():
    service, _resource, _customer = create_service_resource_customer()
    service.name = "<script>alert(1)</script>"
    service.slug = "wax-brow"
    service.save(update_fields=["name", "slug", "updated_at"])
    monday = _future_weekday(0)

    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "normal",
            "service_public_id": str(service.id),
            "start_date": monday.isoformat(),
            "end_date": monday.isoformat(),
        },
        secure=True,
    )

    assert response.status_code == 200
    body = response.json()
    assert "calendar" in body
    assert "<script" not in str(body).lower()
    assert str(service.id) not in str(body["calendar"]["days"])


@pytest.mark.django_db
def test_catalog_resolve_api_rejects_path_traversal():
    response = Client().get(
        "/api/bookings/catalog/resolve/",
        {"selection_type": "normal", "slug": "../../etc/passwd"},
        secure=True,
    )
    assert response.status_code == 400
    assert "passwd" not in response.content.decode().lower()


@pytest.mark.django_db
def test_catalog_resolve_api_returns_package_by_slug():
    package = FullPackage.objects.create(
        name="Relax Package",
        slug="relax-package",
        duration_minutes=150,
        price_amount=Decimal("7000.00"),
    )
    response = Client().get(
        "/api/bookings/catalog/resolve/",
        {"selection_type": "full_package", "slug": "relax-package"},
        secure=True,
    )
    assert response.status_code == 200
    selection = response.json()["selection"]
    assert selection["public_id"] == str(package.public_id)
    assert selection["slug"] == "relax-package"
