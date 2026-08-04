"""Contract tests: every marketing slug resolves and produces a valid calendar."""

from __future__ import annotations

import pytest
from django.core.management import call_command
from django.test import Client

from bookings.domain.calendar import CALENDAR_OFFERED_DAYS_COUNT, OFFERED_WEEKDAYS
from bookings.domain.marketing_catalog import PACKAGE_PLAN_SLUGS, marketing_treatment_cases
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
@pytest.mark.usefixtures("marketing_catalog_seeded")
@pytest.mark.parametrize("plan_slug", PACKAGE_PLAN_SLUGS)
def test_every_package_handoff_resolves_and_calendars(plan_slug):
    selection = resolve_booking_handoff(handoff_type="package", plan_slug=plan_slug)
    assert selection.selection_type == "full_package"
    assert selection.policy_profile == "full_package"
    assert selection.slug == plan_slug

    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "full_package",
            "full_package_public_id": str(selection.public_id),
        },
        secure=True,
    )
    assert response.status_code == 200
    calendar = response.json()["calendar"]
    assert calendar["layout"] == "package_pairs"
    assert len(calendar["days"]) == CALENDAR_OFFERED_DAYS_COUNT
    assert all(day["weekday"] in PACKAGE_WEEKDAYS for day in calendar["days"])
    assert any(day["status"] != "closed" for day in calendar["days"])


@pytest.mark.django_db
@pytest.mark.usefixtures("marketing_catalog_seeded")
@pytest.mark.parametrize(
    "category_slug,treatment_slug,_name",
    marketing_treatment_cases(),
)
def test_every_treatment_handoff_resolves_and_calendars(category_slug, treatment_slug, _name):
    selection = resolve_booking_handoff(
        handoff_type="single",
        category_slug=category_slug,
        treatment_slug=treatment_slug,
    )
    assert selection.selection_type == "normal"
    assert selection.policy_profile == "single"
    assert selection.slug == treatment_slug

    response = Client().get(
        "/api/bookings/calendar/",
        {
            "selection_type": "normal",
            "service_public_id": str(selection.public_id),
        },
        secure=True,
    )
    assert response.status_code == 200
    calendar = response.json()["calendar"]
    assert calendar["layout"] == "singles"
    assert len(calendar["days"]) == CALENDAR_OFFERED_DAYS_COUNT
    assert all(day["weekday"] in SINGLE_WEEKDAYS for day in calendar["days"])
    assert any(day["status"] != "closed" for day in calendar["days"])
