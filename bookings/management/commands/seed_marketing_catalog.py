"""Seed FullPackage and Service rows that match the public marketing site slugs."""

from __future__ import annotations

import re
from decimal import Decimal

from django.core.management.base import BaseCommand

from bookings.models import FullPackage, Service, ServiceCategory

SLUG_RE = re.compile(r"^[a-z0-9-]{1,140}$")

MARKETING_PACKAGES = [
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
]

MARKETING_SERVICES = [
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
]


def slugify_name(name: str) -> str:
    slug = name.lower().replace("&", "and")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    if not SLUG_RE.match(slug):
        raise ValueError(f"Invalid slug for {name!r}: {slug}")
    return slug


class Command(BaseCommand):
    help = "Seed marketing packages and single treatments with stable URL slugs."

    def handle(self, *args, **options):
        package_count = self._seed_packages()
        service_count = self._seed_services()
        self.stdout.write(f"marketing_catalog packages={package_count} services={service_count}")

    def _seed_packages(self) -> int:
        count = 0
        for row in MARKETING_PACKAGES:
            package, _created = FullPackage.objects.update_or_create(
                slug=row["slug"],
                defaults={
                    "name": row["name"],
                    "description": row["name"],
                    "duration_minutes": row["duration_minutes"],
                    "price_amount": row["price_amount"],
                    "currency": "KES",
                    "sort_order": row["sort_order"],
                    "is_active": True,
                },
            )
            if not package.is_active:
                package.is_active = True
                package.save(update_fields=["is_active", "updated_at"])
            count += 1
        return count

    def _seed_services(self) -> int:
        count = 0
        for category_slug, name, duration_minutes, base_price in MARKETING_SERVICES:
            category, _ = ServiceCategory.objects.get_or_create(
                slug=category_slug,
                defaults={"name": category_slug.title(), "sort_order": 1},
            )
            slug = slugify_name(name)
            service, _created = Service.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": category_slug,
                    "category_ref": category,
                    "duration_minutes": duration_minutes,
                    "base_price": base_price,
                    "currency": "KES",
                    "is_active": True,
                },
            )
            if not service.is_active:
                service.is_active = True
                service.save(update_fields=["is_active", "updated_at"])
            count += 1
        return count
