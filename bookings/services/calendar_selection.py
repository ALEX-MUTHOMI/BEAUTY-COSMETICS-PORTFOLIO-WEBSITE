"""Resolve calendar API parameters to a validated BookableSelection."""

from __future__ import annotations

from uuid import UUID

from django.core.exceptions import ValidationError

from bookings.domain.selection import BookableSelection, SelectionType
from bookings.services.bundles import get_full_package_summary, safe_public_text, validate_service_bundle

GENERIC_CALENDAR_ERROR = "Calendar unavailable."


def _normalize_selection_type(value) -> SelectionType:
    normalized = str(value or "normal").strip().lower()
    if normalized not in {"normal", "full_package"}:
        raise ValidationError(GENERIC_CALENDAR_ERROR)
    return normalized  # type: ignore[return-value]


def _has_value(value) -> bool:
    return bool(str(value or "").strip())


def resolve_calendar_selection(
    *,
    selection_type: str,
    service_public_id=None,
    full_package_public_id=None,
) -> BookableSelection:
    """
    Build BookableSelection from calendar query params.

    Rejects type/id mismatches and ambiguous dual-id requests.
    """
    normalized_type = _normalize_selection_type(selection_type)
    has_service = _has_value(service_public_id)
    has_package = _has_value(full_package_public_id)

    if has_service and has_package:
        raise ValidationError(GENERIC_CALENDAR_ERROR)

    if normalized_type == "full_package":
        if not has_package:
            raise ValidationError(GENERIC_CALENDAR_ERROR)
        summary = get_full_package_summary(full_package_public_id)
        package = summary.full_package
        turnaround = summary.buffer_before_minutes + summary.buffer_after_minutes
        return BookableSelection.from_parts(
            selection_type="full_package",
            public_id=package.public_id,
            slug=package.slug,
            name=safe_public_text(package.name),
            duration_minutes=package.duration_minutes,
            turnaround_minutes=turnaround,
        )

    if not has_service:
        raise ValidationError(GENERIC_CALENDAR_ERROR)
    summary = validate_service_bundle([service_public_id])
    service = summary.items[0].service
    turnaround = summary.buffer_before_minutes + summary.buffer_after_minutes
    return BookableSelection.from_parts(
        selection_type="normal",
        public_id=UUID(str(service.id)),
        slug=service.slug,
        name=safe_public_text(service.name),
        duration_minutes=service.duration_minutes,
        turnaround_minutes=turnaround,
    )
