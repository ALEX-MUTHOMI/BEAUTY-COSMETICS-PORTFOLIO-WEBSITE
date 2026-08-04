from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.utils import timezone

from bookings.models import BookableResource, BusinessHours, CustomerProfile

NAIROBI = ZoneInfo("Africa/Nairobi")
UTC = ZoneInfo("UTC")


def eat_datetime(year, month, day, hour, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=NAIROBI)


def utc_from_eat(year, month, day, hour, minute=0):
    return eat_datetime(year, month, day, hour, minute).astimezone(UTC)


def future_monday():
    return utc_from_eat(2030, 6, 3, 9)


def future_tuesday():
    # Package hybrid anchors start at studio open (07:00), not 09:00.
    return utc_from_eat(2030, 6, 4, 7)


def future_wednesday():
    return utc_from_eat(2030, 6, 5, 9)


def make_resource():
    resource = BookableResource.objects.create(
        name=f"Beautician {timezone.now().timestamp()}",
        resource_type=BookableResource.Type.BEAUTICIAN,
    )
    BusinessHours.create_default_week(resource=resource)
    return resource


def make_customer_payload():
    return {
        "full_name": "Grace Wanjiku",
        "email": "grace@example.com",
        "phone": "+254712345678",
    }


def make_customer():
    return CustomerProfile.create_from_plaintext(**make_customer_payload())


def money(value):
    return Decimal(value).quantize(Decimal("0.01"))
