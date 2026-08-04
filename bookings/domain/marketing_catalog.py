"""Canonical marketing catalog slugs — must match frontend bookingCatalog.ts and seed command."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Literal

CategorySlug = Literal["facials", "massage", "waxing", "makeup"]

SLUG_RE = re.compile(r"^[a-z0-9-]{1,140}$")

MARKETING_PACKAGES: tuple[dict, ...] = (
    {
        "name": "Classic Full Package",
        "slug": "classic-full-package",
        "duration_minutes": 240,
        "price_amount": Decimal("12000.00"),
        "sort_order": 1,
    },
    {
        "name": "Glow Package",
        "slug": "glow-package",
        "duration_minutes": 180,
        "price_amount": Decimal("8500.00"),
        "sort_order": 2,
    },
    {
        "name": "Relax Package",
        "slug": "relax-package",
        "duration_minutes": 150,
        "price_amount": Decimal("7000.00"),
        "sort_order": 3,
    },
)

MARKETING_SERVICES: tuple[tuple[CategorySlug, str, int, Decimal], ...] = (
    ("facials", "Deep cleansing facial", 60, Decimal("2500.00")),
    ("facials", "Brightening facial", 60, Decimal("3000.00")),
    ("facials", "Hydrating facial", 60, Decimal("2800.00")),
    ("facials", "Express facial", 30, Decimal("1800.00")),
    ("facials", "Anti-ageing rejuvenation", 75, Decimal("3500.00")),
    ("massage", "Swedish massage", 60, Decimal("3000.00")),
    ("massage", "Deep tissue massage", 60, Decimal("3500.00")),
    ("massage", "Back, neck & shoulders", 30, Decimal("2200.00")),
    ("massage", "Hot stone massage", 60, Decimal("4000.00")),
    ("waxing", "Brow shaping", 20, Decimal("800.00")),
    ("waxing", "Upper lip & chin", 15, Decimal("600.00")),
    ("waxing", "Underarms", 15, Decimal("1200.00")),
    ("waxing", "Half leg", 30, Decimal("1500.00")),
    ("waxing", "Full leg", 45, Decimal("2500.00")),
    ("waxing", "Bikini & Brazilian", 45, Decimal("2000.00")),
    ("waxing", "Full body wax", 90, Decimal("6500.00")),
    ("makeup", "Everyday makeup", 45, Decimal("4000.00")),
    ("makeup", "Soft glam", 60, Decimal("5500.00")),
    ("makeup", "Bridal & event glam", 90, Decimal("8000.00")),
    ("makeup", "Evening & photography makeup", 75, Decimal("6500.00")),
)

PACKAGE_PLAN_SLUGS: tuple[str, ...] = tuple(row["slug"] for row in MARKETING_PACKAGES)


def slugify_name(name: str) -> str:
    slug = name.lower().replace("&", "and")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    if not SLUG_RE.match(slug):
        raise ValueError(f"Invalid slug for {name!r}: {slug}")
    return slug


def marketing_treatment_cases() -> list[tuple[CategorySlug, str, str]]:
    """(category_slug, treatment_slug, display_name) for every single treatment."""
    return [(category, slugify_name(name), name) for category, name, _duration, _price in MARKETING_SERVICES]
