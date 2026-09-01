from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError

from bookings.models import FullPackage, Service
from bookings.privacy import strip_markup

GENERIC_SELECTION_ERROR = "Booking selection unavailable."


def safe_public_text(value, max_length=128):
    return strip_markup(value, max_length=max_length)


@dataclass(frozen=True)
class SelectionItem:
    service: Service
    name: str
    category: str
    duration_minutes: int
    buffer_before_minutes: int
    buffer_after_minutes: int
    price: Decimal
    currency: str


@dataclass(frozen=True)
class SelectionSummary:
    selection_type: str
    items: tuple[SelectionItem, ...]
    total_duration_minutes: int
    buffer_before_minutes: int
    buffer_after_minutes: int
    total_price: Decimal
    currency: str
    full_package: FullPackage | None = None

    @property
    def public_snapshot(self):
        if self.full_package:
            return {
                "type": "full_package",
                "package_public_id": str(self.full_package.public_id),
                "name": safe_public_text(self.full_package.name),
                "duration_minutes": self.total_duration_minutes,
                "total_price": f"{self.total_price:.2f}",
                "currency": self.currency,
            }
        return {
            "type": "normal_bundle",
            "items": [
                {
                    "service_public_id": str(item.service.id),
                    "name": item.name,
                    "category": item.category,
                    "duration_minutes": item.duration_minutes,
                    "price": f"{item.price:.2f}",
                    "currency": item.currency,
                }
                for item in self.items
            ],
            "duration_minutes": self.total_duration_minutes,
            "total_price": f"{self.total_price:.2f}",
            "currency": self.currency,
        }


def _services_for_public_ids(service_public_ids):
    if not service_public_ids:
        raise ValidationError(GENERIC_SELECTION_ERROR)
    normalized_ids = [str(value) for value in service_public_ids]
    if len(set(normalized_ids)) != len(normalized_ids):
        raise ValidationError(GENERIC_SELECTION_ERROR)
    services = list(
        Service.objects.select_related("category_ref", "subcategory").filter(id__in=normalized_ids, is_active=True)
    )
    if len(services) != len(normalized_ids):
        raise ValidationError(GENERIC_SELECTION_ERROR)
    by_id = {str(service.id): service for service in services}
    return [by_id[value] for value in normalized_ids]


def validate_service_bundle(service_public_ids, client_amount=None):
    services = _services_for_public_ids(service_public_ids)
    if len(services) > 4:
        raise ValidationError(GENERIC_SELECTION_ERROR)

    categories: dict[str, int] = {}
    currencies = {getattr(service, "currency", "KES") for service in services}
    if len(currencies) != 1:
        raise ValidationError(GENERIC_SELECTION_ERROR)
    for service in services:
        category_key = str(service.category_ref_id or service.category)
        categories[category_key] = categories.get(category_key, 0) + 1

    category_count = len(categories)
    if category_count > 3:
        raise ValidationError(GENERIC_SELECTION_ERROR)
    if category_count == 3 and any(count > 1 for count in categories.values()):
        raise ValidationError(GENERIC_SELECTION_ERROR)
    if category_count in {1, 2} and any(count > 2 for count in categories.values()):
        raise ValidationError(GENERIC_SELECTION_ERROR)

    items = tuple(
        SelectionItem(
            service=service,
            name=safe_public_text(service.name),
            category=safe_public_text(service.category_ref.name if service.category_ref else service.category),
            duration_minutes=service.duration_minutes,
            buffer_before_minutes=service.buffer_before_minutes,
            buffer_after_minutes=service.buffer_after_minutes,
            price=service.base_price.quantize(Decimal("0.01")),
            currency=service.currency,
        )
        for service in services
    )
    return SelectionSummary(
        selection_type="normal",
        items=items,
        total_duration_minutes=sum(item.duration_minutes for item in items),
        buffer_before_minutes=max((item.buffer_before_minutes for item in items), default=0),
        buffer_after_minutes=sum(item.buffer_after_minutes for item in items),
        total_price=sum((item.price for item in items), Decimal("0.00")).quantize(Decimal("0.01")),
        currency=items[0].currency,
    )


def get_full_package_summary(full_package_public_id):
    try:
        package = FullPackage.objects.get(public_id=full_package_public_id, is_active=True)
    except (FullPackage.DoesNotExist, TypeError, ValueError) as exc:
        raise ValidationError(GENERIC_SELECTION_ERROR) from exc
    return SelectionSummary(
        selection_type="full_package",
        items=(),
        total_duration_minutes=package.duration_minutes,
        buffer_before_minutes=0,
        buffer_after_minutes=package.buffer_after_minutes,
        total_price=package.price_amount.quantize(Decimal("0.01")),
        currency=package.currency,
        full_package=package,
    )


def list_public_services(service_public_ids=None):
    queryset = Service.objects.select_related("category_ref", "subcategory").filter(is_active=True)
    if service_public_ids is not None:
        queryset = queryset.filter(id__in=[str(value) for value in service_public_ids])
    services = list(queryset.order_by("sort_order", "name"))
    if service_public_ids is not None and len(services) != len(set(service_public_ids)):
        raise ValidationError(GENERIC_SELECTION_ERROR)
    return [
        {
            "public_id": str(service.id),
            "name": safe_public_text(service.name),
            "category": safe_public_text(service.category_ref.name if service.category_ref else service.category),
            "subcategory": safe_public_text(service.subcategory.name if service.subcategory else ""),
            "duration_minutes": service.duration_minutes,
            "price": f"{service.base_price:.2f}",
            "currency": service.currency,
        }
        for service in services
    ]


def list_public_full_packages():
    return [
        {
            "public_id": str(package.public_id),
            "name": safe_public_text(package.name),
            "description": safe_public_text(package.description, 240),
            "duration_minutes": package.duration_minutes,
            "price": f"{package.price_amount:.2f}",
            "currency": package.currency,
        }
        for package in FullPackage.objects.filter(is_active=True).order_by("sort_order", "name")
    ]
