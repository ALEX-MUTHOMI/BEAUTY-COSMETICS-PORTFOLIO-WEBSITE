"""Compatibility wrapper for the public bookings API adapter.

New code should import from ``bookings.api.public_views``. This module remains
to keep existing imports stable during incremental backend modularization.
"""

from bookings.api.public_views import (  # noqa: F401
    booking_availability,
    booking_checkout_create,
    booking_hold_create,
    booking_policy_acceptance_text,
    catalog_packages,
    catalog_services,
)
