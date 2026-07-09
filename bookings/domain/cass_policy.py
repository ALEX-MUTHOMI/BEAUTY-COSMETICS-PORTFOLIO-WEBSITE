"""CASS production policy — Option A: type-level rules only, no per-slug overrides."""

from __future__ import annotations

from bookings.domain.calendar import OFFERED_WEEKDAYS

CASS_POLICY_MODE = "type_level_only"
CASS_POLICY_LABEL = "Option A — type-level weekdays and capacity only"

PACKAGE_OFFERED_WEEKDAYS = OFFERED_WEEKDAYS["full_package"]
SINGLE_OFFERED_WEEKDAYS = OFFERED_WEEKDAYS["normal"]


def active_service_day_rule_count() -> int:
    from bookings.models import ServiceDayRule

    return ServiceDayRule.objects.filter(is_active=True).count()


def assert_option_a_catalog_invariant() -> None:
    """Production catalog must not ship active per-slug calendar overrides."""
    count = active_service_day_rule_count()
    if count:
        raise AssertionError(
            f"CASS Option A violated: {count} active ServiceDayRule row(s) exist; "
            "every service must follow type-level package/single rules only."
        )
