from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from bookings.models import BookableResource, Booking, BusinessHours, CustomerProfile, Service


def create_customer_profile(full_name="Grace Wanjiku", email="grace@example.com", phone="+254712345678"):
    return CustomerProfile.create_from_plaintext(
        full_name=full_name,
        email=email,
        phone=phone,
        reminder_consent=True,
    )


def create_service_resource_customer():
    service = Service.objects.create(
        name="Makeup session",
        slug=f"makeup-session-{timezone.now().timestamp()}",
        category="makeup",
        duration_minutes=60,
        base_price=Decimal("2500.00"),
    )
    resource = BookableResource.objects.create(name=f"Chair {timezone.now().timestamp()}", resource_type="chair")
    BusinessHours.create_default_week(resource=resource)
    customer = create_customer_profile()
    return service, resource, customer


def create_booking(**overrides):
    service, resource, customer = create_service_resource_customer()
    starts_at = overrides.pop(
        "starts_at", timezone.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=5)
    )
    ends_at = overrides.pop("ends_at", starts_at + timedelta(minutes=service.duration_minutes))
    return Booking.objects.create(
        customer_profile=overrides.pop("customer_profile", customer),
        service=overrides.pop("service", service),
        resource=overrides.pop("resource", resource),
        starts_at=starts_at,
        ends_at=ends_at,
        idempotency_key=overrides.pop("idempotency_key", f"booking-{timezone.now().timestamp()}"),
        **overrides,
    )
