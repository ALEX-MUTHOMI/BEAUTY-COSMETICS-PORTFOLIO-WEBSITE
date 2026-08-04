"""Seed FullPackage and Service rows that match the public marketing site slugs."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from bookings.domain.marketing_catalog import MARKETING_PACKAGES, MARKETING_SERVICES, slugify_name
from bookings.models import FullPackage, Service, ServiceCategory


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
