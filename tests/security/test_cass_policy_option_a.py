"""CASS Option A — type-level policy only; zero per-slug overrides in production catalog."""

from __future__ import annotations

import pytest
from django.core.management import call_command
from django.test import Client

from bookings.domain.calendar import CALENDAR_OFFERED_DAYS_COUNT, OFFERED_WEEKDAYS
from bookings.domain.cass_policy import (
    CASS_POLICY_MODE,
    assert_option_a_catalog_invariant,
)
from bookings.domain.marketing_catalog import PACKAGE_PLAN_SLUGS, marketing_treatment_cases
from bookings.models import ServiceDayRule
from bookings.services.handoff_resolve import resolve_booking_handoff
from bookings.tests.factories import create_service_resource_customer

PACKAGE_WEEKDAYS = OFFERED_WEEKDAYS["full_package"]
SINGLE_WEEKDAYS = OFFERED_WEEKDAYS["normal"]


@pytest.fixture(scope="module")
def marketing_catalog_seeded(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        create_service_resource_customer()
        call_command("seed_marketing_catalog")


@pytest.mark.django_db
def test_cass_policy_mode_is_type_level_only():
    assert CASS_POLICY_MODE == "type_level_only"


@pytest.mark.django_db
@pytest.mark.usefixtures("marketing_catalog_seeded")
def test_marketing_catalog_seed_has_zero_service_day_rules():
    assert_option_a_catalog_invariant()
    assert ServiceDayRule.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.usefixtures("marketing_catalog_seeded")
@pytest.mark.parametrize("plan_slug", PACKAGE_PLAN_SLUGS)
def test_every_package_uses_canonical_weekdays_only(plan_slug):
    selection = resolve_booking_handoff(handoff_type="package", plan_slug=plan_slug)
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "full_package",
            "full_package_public_id": str(selection.public_id),
        },
        secure=True,
    )
    assert response.status_code == 200
    weekdays = {day["weekday"] for day in response.json()["calendar"]["days"]}
    assert weekdays.issubset(PACKAGE_WEEKDAYS)
    assert len(response.json()["calendar"]["days"]) == CALENDAR_OFFERED_DAYS_COUNT


@pytest.mark.django_db
@pytest.mark.usefixtures("marketing_catalog_seeded")
@pytest.mark.parametrize("category_slug,treatment_slug,_name", marketing_treatment_cases())
def test_every_single_uses_canonical_weekdays_only(category_slug, treatment_slug, _name):
    selection = resolve_booking_handoff(
        handoff_type="single",
        category_slug=category_slug,
        treatment_slug=treatment_slug,
    )
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "normal",
            "service_public_id": str(selection.public_id),
        },
        secure=True,
    )
    assert response.status_code == 200
    weekdays = {day["weekday"] for day in response.json()["calendar"]["days"]}
    assert weekdays.issubset(SINGLE_WEEKDAYS)
    assert len(response.json()["calendar"]["days"]) == CALENDAR_OFFERED_DAYS_COUNT


@pytest.mark.django_db
@pytest.mark.usefixtures("marketing_catalog_seeded")
def test_public_calendar_cannot_inject_service_day_rule_via_query():
    selection = resolve_booking_handoff(handoff_type="package", plan_slug="classic-full-package")
    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "full_package",
            "full_package_public_id": str(selection.public_id),
            "catalog_slug": "classic-full-package",
            "weekday": "0",
            "offered": "true",
            "max_clients": "99",
        },
        secure=True,
    )
    assert response.status_code == 200
    weekdays = {day["weekday"] for day in response.json()["calendar"]["days"]}
    assert 0 not in weekdays
    assert_option_a_catalog_invariant()
