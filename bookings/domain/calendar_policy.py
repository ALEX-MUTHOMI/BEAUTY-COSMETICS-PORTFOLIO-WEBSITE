"""Calendar policy — selection-aware rules for a single local date."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, time

from bookings.domain.calendar import weekdays_for_policy_profile
from bookings.domain.selection import BookableSelection, PolicyProfile
from bookings.models import BookingDayPolicy
from bookings.services.day_policy import default_policy_for_date
from bookings.services.service_day_rules import lookup_service_day_rule


@dataclass(frozen=True)
class CalendarDayPolicy:
    day_type: str
    offered: bool
    max_clients: int
    normal_bookings_allowed: bool
    full_package_allowed: bool
    business_start: time
    business_end: time

    @classmethod
    def from_booking_day_policy(
        cls,
        *,
        policy: BookingDayPolicy,
        offered: bool,
    ) -> CalendarDayPolicy:
        max_clients = 0 if policy.day_type == BookingDayPolicy.DayType.CLOSED else policy.max_clients
        return cls(
            day_type=policy.day_type,
            offered=offered,
            max_clients=max_clients,
            normal_bookings_allowed=policy.normal_bookings_allowed,
            full_package_allowed=policy.full_package_allowed,
            business_start=policy.business_start_time,
            business_end=policy.business_end_time,
        )

    def classification_payload(self) -> dict:
        """Fields consumed by classify_calendar_day (no business hours)."""
        return {
            "day_type": self.day_type,
            "normal_bookings_allowed": self.normal_bookings_allowed,
            "full_package_allowed": self.full_package_allowed,
            "max_clients": self.max_clients,
        }


class CalendarPolicy:
    @staticmethod
    def for_date(*, selection: BookableSelection, local_date: date) -> CalendarDayPolicy:
        """
        Effective policy for *selection* on *local_date*.

        Phase 3b: studio day policy + policy_profile weekday gate.
        Phase 3e: optional per-slug overrides.
        """
        base = default_policy_for_date(local_date)
        offered = local_date.weekday() in weekdays_for_policy_profile(selection.policy_profile)
        policy = CalendarDayPolicy.from_booking_day_policy(policy=base, offered=offered)
        rule = lookup_service_day_rule(selection=selection, local_date=local_date)
        if not rule:
            return policy
        overrides = {}
        if rule.offered is not None:
            overrides["offered"] = rule.offered
        if rule.max_clients is not None:
            overrides["max_clients"] = rule.max_clients
        if overrides:
            return replace(policy, **overrides)
        return policy

    @staticmethod
    def is_weekday_offered(*, policy_profile: PolicyProfile, local_date: date) -> bool:
        return local_date.weekday() in weekdays_for_policy_profile(policy_profile)
