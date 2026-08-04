"""Lookup optional per-slug calendar overrides (Phase 3e)."""

from __future__ import annotations

from datetime import date

from bookings.domain.calendar import weekdays_for_policy_profile
from bookings.domain.selection import BookableSelection
from bookings.models import ServiceDayRule


def lookup_service_day_rule(*, selection: BookableSelection, local_date: date) -> ServiceDayRule | None:
    return (
        ServiceDayRule.objects.filter(
            selection_type=selection.selection_type,
            catalog_slug=selection.slug,
            weekday=local_date.weekday(),
            is_active=True,
        )
        .order_by("-updated_at")
        .first()
    )


def offered_weekdays_for_selection(selection: BookableSelection) -> frozenset[int]:
    """Type-level weekdays plus optional per-slug ServiceDayRule adjustments."""
    weekdays = set(weekdays_for_policy_profile(selection.policy_profile))
    rules = ServiceDayRule.objects.filter(
        selection_type=selection.selection_type,
        catalog_slug=selection.slug,
        is_active=True,
    )
    for rule in rules:
        if rule.offered is True:
            weekdays.add(rule.weekday)
        elif rule.offered is False:
            weekdays.discard(rule.weekday)
    return frozenset(weekdays)
