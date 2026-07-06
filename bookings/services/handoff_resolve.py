"""Resolve public /book handoff tokens to catalog selections (server-side only)."""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError

from bookings.models import Service
from bookings.services.catalog_resolve import SLUG_RE, _normalize_slug, resolve_catalog_selection

GENERIC_HANDOFF_ERROR = "Selection unavailable."

ALLOWED_HANDOFF_TYPES = {"package", "single"}
ALLOWED_CATEGORY_SLUGS = {"facials", "massage", "waxing", "makeup"}

CATEGORY_KEYWORDS = {
    "facials": ("facial", "skin", "cleanse"),
    "massage": ("massage", "tissue", "swedish"),
    "waxing": ("wax", "brow", "brazilian", "bikini"),
    "makeup": ("makeup", "glam", "bridal"),
}


def _category_slug(value) -> str:
    slug = _normalize_slug(value)
    if slug not in ALLOWED_CATEGORY_SLUGS:
        raise ValidationError(GENERIC_HANDOFF_ERROR)
    return slug


def _service_matches_category(service: Service, category_slug: str) -> bool:
    haystack = f"{service.slug} {service.name} {service.category}".lower()
    return any(keyword in haystack for keyword in CATEGORY_KEYWORDS[category_slug])


def resolve_booking_handoff(*, handoff_type: str, plan_slug=None, category_slug=None, treatment_slug=None) -> dict:
    normalized_type = str(handoff_type or "").strip().lower()
    if normalized_type not in ALLOWED_HANDOFF_TYPES:
        raise ValidationError(GENERIC_HANDOFF_ERROR)

    if normalized_type == "package":
        if not plan_slug:
            raise ValidationError(GENERIC_HANDOFF_ERROR)
        return resolve_catalog_selection(selection_type="full_package", slug=plan_slug)

    category = _category_slug(category_slug)
    queryset = Service.objects.filter(is_active=True).select_related("category_ref")

    if treatment_slug:
        treatment = _normalize_slug(treatment_slug)
        service = queryset.filter(slug=treatment).first()
        if not service or not _service_matches_category(service, category):
            raise ValidationError(GENERIC_HANDOFF_ERROR)
        return resolve_catalog_selection(selection_type="normal", slug=service.slug)

    for service in queryset.order_by("sort_order", "name"):
        if _service_matches_category(service, category):
            return resolve_catalog_selection(selection_type="normal", slug=service.slug)

    raise ValidationError(GENERIC_HANDOFF_ERROR)
