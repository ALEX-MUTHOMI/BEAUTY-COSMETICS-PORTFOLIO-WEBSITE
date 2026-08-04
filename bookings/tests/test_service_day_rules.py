"""Phase 3e — optional per-slug ServiceDayRule overrides."""

from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.test import Client

from bookings.domain.calendar_policy import CalendarPolicy
from bookings.domain.selection import BookableSelection
from bookings.models import ServiceDayRule
from bookings.services.booking_calendar import BookingCalendarService
from bookings.services.service_day_rules import offered_weekdays_for_selection
from bookings.tests.factories import create_service_resource_customer


def _selection(*, slug: str, selection_type: str = "normal") -> BookableSelection:
    service, _resource, _customer = create_service_resource_customer()
    service.slug = slug
    service.save(update_fields=["slug", "updated_at"])
    return BookableSelection.from_parts(
        selection_type=selection_type,  # type: ignore[arg-type]
        public_id=service.id,
        slug=slug,
        name=service.name,
        duration_minutes=service.duration_minutes,
    )


@pytest.mark.django_db
def test_without_service_day_rules_type_defaults_unchanged():
    selection = _selection(slug="phase-3e-default-single")
    monday = date(2030, 6, 3)
    tuesday = date(2030, 6, 4)

    assert CalendarPolicy.for_date(selection=selection, local_date=monday).offered is True
    assert CalendarPolicy.for_date(selection=selection, local_date=tuesday).offered is False
    assert offered_weekdays_for_selection(selection) == frozenset({0, 3, 4, 5})


@pytest.mark.django_db
def test_service_day_rule_can_offer_extra_weekday_for_one_slug():
    selection = _selection(slug="phase-3e-tuesday-single")
    ServiceDayRule.objects.create(
        selection_type=ServiceDayRule.SelectionType.NORMAL,
        catalog_slug=selection.slug,
        weekday=1,
        offered=True,
        is_active=True,
    )
    tuesday = date(2030, 6, 4)

    policy = CalendarPolicy.for_date(selection=selection, local_date=tuesday)
    assert policy.offered is True
    assert 1 in offered_weekdays_for_selection(selection)


@pytest.mark.django_db
def test_service_day_rule_can_suppress_default_weekday_for_one_slug():
    selection = _selection(slug="phase-3e-no-monday-single")
    ServiceDayRule.objects.create(
        selection_type=ServiceDayRule.SelectionType.NORMAL,
        catalog_slug=selection.slug,
        weekday=0,
        offered=False,
        is_active=True,
    )
    monday = date(2030, 6, 3)

    assert CalendarPolicy.for_date(selection=selection, local_date=monday).offered is False
    assert 0 not in offered_weekdays_for_selection(selection)


@pytest.mark.django_db
def test_service_day_rule_max_clients_override_applies_to_calendar():
    selection = _selection(slug="phase-3e-capacity-single")
    ServiceDayRule.objects.create(
        selection_type=ServiceDayRule.SelectionType.NORMAL,
        catalog_slug=selection.slug,
        weekday=0,
        max_clients=1,
        is_active=True,
    )
    monday = date(2030, 6, 3)

    policy = CalendarPolicy.for_date(selection=selection, local_date=monday)
    assert policy.max_clients == 1

    payload = BookingCalendarService.build_calendar_for_selection(
        selection=selection,
        start_date=monday,
        end_date=monday + timedelta(days=6),
    )
    monday_day = next(day for day in payload["days"] if day["date"] == monday.isoformat())
    assert monday_day["capacity"]["max"] == 1


@pytest.mark.django_db
def test_service_day_rule_requires_at_least_one_override_field():
    rule = ServiceDayRule(
        selection_type=ServiceDayRule.SelectionType.NORMAL,
        catalog_slug="invalid-rule",
        weekday=0,
        is_active=True,
    )
    with pytest.raises(ValidationError):
        rule.full_clean()


@pytest.mark.django_db
def test_other_slugs_ignore_unrelated_service_day_rules():
    selection_a = _selection(slug="phase-3e-slug-a")
    selection_b = _selection(slug="phase-3e-slug-b")
    ServiceDayRule.objects.create(
        selection_type=ServiceDayRule.SelectionType.NORMAL,
        catalog_slug=selection_a.slug,
        weekday=1,
        offered=True,
        is_active=True,
    )
    tuesday = date(2030, 6, 4)

    assert CalendarPolicy.for_date(selection=selection_a, local_date=tuesday).offered is True
    assert CalendarPolicy.for_date(selection=selection_b, local_date=tuesday).offered is False


@pytest.mark.django_db
def test_production_catalog_seed_has_zero_service_day_rules():
    from bookings.domain.cass_policy import assert_option_a_catalog_invariant

    assert_option_a_catalog_invariant()


@pytest.mark.django_db
def test_public_calendar_api_cannot_set_service_day_rules_via_query():
    service, _resource, _customer = create_service_resource_customer()
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "normal",
            "service_public_id": str(service.id),
            "catalog_slug": service.slug,
            "weekday": "1",
            "offered": "true",
            "max_clients": "99",
        },
        secure=True,
    )
    assert response.status_code == 200
    assert ServiceDayRule.objects.count() == 0
