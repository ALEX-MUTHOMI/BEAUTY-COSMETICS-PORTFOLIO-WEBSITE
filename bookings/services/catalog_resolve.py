from __future__ import annotations

import re

from django.core.exceptions import ValidationError

from bookings.models import FullPackage, Service
from bookings.services.bundles import safe_public_text

GENERIC_RESOLVE_ERROR = "Selection unavailable."
SLUG_RE = re.compile(r"^[a-z0-9-]{1,140}$")


def _normalize_slug(value) -> str:
    slug = str(value or "").strip().lower()
    if not slug or not SLUG_RE.match(slug):
        raise ValidationError(GENERIC_RESOLVE_ERROR)
    return slug


def resolve_catalog_selection(*, selection_type: str, slug: str) -> dict:
    normalized_type = str(selection_type or "").strip().lower()
    normalized_slug = _normalize_slug(slug)

    if normalized_type == "full_package":
        try:
            package = FullPackage.objects.get(slug=normalized_slug, is_active=True)
        except FullPackage.DoesNotExist as exc:
            raise ValidationError(GENERIC_RESOLVE_ERROR) from exc
        return {
            "selection_type": "full_package",
            "public_id": str(package.public_id),
            "slug": package.slug,
            "name": safe_public_text(package.name),
            "duration_minutes": package.duration_minutes,
        }

    if normalized_type == "normal":
        try:
            service = Service.objects.select_related("category_ref").get(slug=normalized_slug, is_active=True)
        except Service.DoesNotExist as exc:
            raise ValidationError(GENERIC_RESOLVE_ERROR) from exc
        return {
            "selection_type": "normal",
            "public_id": str(service.id),
            "slug": service.slug,
            "name": safe_public_text(service.name),
            "duration_minutes": service.duration_minutes,
        }

    raise ValidationError(GENERIC_RESOLVE_ERROR)
