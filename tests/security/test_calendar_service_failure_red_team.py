"""Red-team: calendar service internal failures must not leak internals or 5xx."""

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import OperationalError
from django.test import Client

from bookings.services.booking_calendar import BookingCalendarService
from bookings.tests.factories import create_service_resource_customer

GENERIC_CALENDAR = "Calendar unavailable."
FORBIDDEN_MARKERS = (
    "traceback",
    "/app/",
    "operationalerror",
    "postgres",
    "secret",
    "password",
    "stack",
)


def _calendar_get(client, **params):
    return client.get("/api/bookings/calendar/", params, secure=True)


@pytest.mark.django_db
def test_calendar_survives_availability_slot_engine_failure(monkeypatch):
    service, _resource, _customer = create_service_resource_customer()

    def boom(*_args, **_kwargs):
        raise RuntimeError("simulated slot engine failure")

    monkeypatch.setattr(
        "bookings.services.booking_calendar.AvailabilityService.get_available_slots",
        boom,
    )
    response = _calendar_get(
        Client(),
        selection_type="normal",
        service_public_id=str(service.id),
    )
    assert response.status_code == 200
    calendar = response.json()["calendar"]
    assert len(calendar["days"]) == 8
    assert all(day["slot_count"] == 0 for day in calendar["days"])
    body = response.content.decode().lower()
    for marker in FORBIDDEN_MARKERS:
        assert marker not in body


@pytest.mark.django_db
def test_calendar_survives_bulk_capacity_query_failure(monkeypatch):
    service, _resource, _customer = create_service_resource_customer()

    def boom(*_args, **_kwargs):
        raise OperationalError("simulated database outage")

    monkeypatch.setattr(
        "bookings.services.booking_calendar._count_blocking_clients_bulk",
        boom,
    )
    response = _calendar_get(
        Client(),
        selection_type="normal",
        service_public_id=str(service.id),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == GENERIC_CALENDAR


@pytest.mark.django_db
def test_calendar_api_never_returns_5xx_on_build_calendar_exception(monkeypatch):
    service, _resource, _customer = create_service_resource_customer()

    def boom(*_args, **_kwargs):
        raise ValidationError("internal calendar fault")

    monkeypatch.setattr(BookingCalendarService, "build_calendar", boom)
    response = _calendar_get(
        Client(),
        selection_type="normal",
        service_public_id=str(service.id),
    )
    assert response.status_code == 400
    assert response.json() == {"detail": GENERIC_CALENDAR}


@pytest.mark.django_db
def test_calendar_api_fails_closed_on_unhandled_build_exception(monkeypatch):
    service, _resource, _customer = create_service_resource_customer()

    def boom(*_args, **_kwargs):
        raise RuntimeError("unhandled calendar regression")

    monkeypatch.setattr(BookingCalendarService, "build_calendar", boom)
    response = _calendar_get(
        Client(),
        selection_type="normal",
        service_public_id=str(service.id),
    )
    assert response.status_code < 500
    assert response.json()["detail"] == GENERIC_CALENDAR
    assert "unhandled calendar regression" not in response.content.decode()


@pytest.mark.django_db
def test_calendar_throttle_still_generic_when_redis_admission_fails(monkeypatch):
    from core.throttling import RouteRateThrottle, ThrottleInfrastructureUnavailable

    service, _resource, _customer = create_service_resource_customer()
    client = Client()

    def broken_allow(*_args, **_kwargs):
        raise ThrottleInfrastructureUnavailable()

    monkeypatch.setattr(RouteRateThrottle, "allow_request", broken_allow)
    response = _calendar_get(
        client,
        selection_type="normal",
        service_public_id=str(service.id),
    )
    assert response.status_code == 503
    assert response.json() == {"detail": "Service temporarily unavailable."}
    assert "redis" not in response.content.decode().lower()


@pytest.mark.django_db
def test_resolve_handoff_fails_closed_when_resolver_raises(monkeypatch):
    def boom(*_args, **_kwargs):
        raise RuntimeError("resolver exploded")

    monkeypatch.setattr(
        "bookings.api.public_views.resolve_booking_handoff",
        boom,
    )
    response = Client().get(
        "/api/bookings/catalog/resolve-handoff/",
        {"type": "package", "plan": "classic-full-package"},
        secure=True,
    )
    assert response.status_code < 500
    assert response.json()["detail"] == "Selection unavailable."
    assert "resolver exploded" not in response.content.decode()
