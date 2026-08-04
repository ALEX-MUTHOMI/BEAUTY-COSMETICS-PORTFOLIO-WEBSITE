"""Compatibility wrapper. Canonical factories live in tests.factories.booking_factories."""

from tests.factories.booking_factories import (  # noqa: F401
    create_booking,
    create_customer_profile,
    create_service_resource_customer,
)

__all__ = ["create_booking", "create_customer_profile", "create_service_resource_customer"]
