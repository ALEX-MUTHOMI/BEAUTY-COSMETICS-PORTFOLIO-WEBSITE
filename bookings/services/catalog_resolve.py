from __future__ import annotations

import re
from uuid import UUID

from django.core.exceptions import ValidationError

from bookings.domain.selection import BookableSelection, SelectionType
from bookings.models import FullPackage, Service
from bookings.services.bundles import safe_public_text

GENERIC_RESOLVE_ERROR = "Selection unavailable."
SLUG_RE = re.compile(r"^[a-z0-9-]{1,140}$")


def _normalize_slug(value) -> str:
    slug = str(value or "").strip().lower()
    if not slug or not SLUG_RE.match(slug):
        raise ValidationError(GENERIC_RESOLVE_ERROR)
    return slug


def _normalize_selection_type(value) -> SelectionType:
    normalized = str(value or "").strip().lower()
    if normalized not in {"normal", "full_package"}:
        raise ValidationError(GENERIC_RESOLVE_ERROR)
    return normalized  # type: ignore[return-value]


def resolve_catalog_selection(*, selection_type: str, slug: str) -> BookableSelection:
    normalized_type = _normalize_selection_type(selection_type)
    normalized_slug = _normalize_slug(slug)

    if normalized_type == "full_package":
        try:
            package = FullPackage.objects.get(slug=normalized_slug, is_active=True)
        except FullPackage.DoesNotExist as exc:
            raise ValidationError(GENERIC_RESOLVE_ERROR) from exc
        return BookableSelection.from_parts(
            selection_type="full_package",
            public_id=package.public_id,
            slug=package.slug,
            name=safe_public_text(package.name),
            duration_minutes=package.duration_minutes,
        )

    try:
        service = Service.objects.select_related("category_ref").get(slug=normalized_slug, is_active=True)
    except Service.DoesNotExist as exc:
        raise ValidationError(GENERIC_RESOLVE_ERROR) from exc
    return BookableSelection.from_parts(
        selection_type="normal",
        public_id=UUID(str(service.id)),
        slug=service.slug,
        name=safe_public_text(service.name),
        duration_minutes=service.duration_minutes,
    )
