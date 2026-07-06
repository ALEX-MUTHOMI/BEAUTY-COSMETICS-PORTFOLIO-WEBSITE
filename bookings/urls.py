from django.urls import path

from bookings.api import public_views
from bookings.views import booking_status

urlpatterns = [
    path("catalog/services/", public_views.catalog_services, name="booking-catalog-services"),
    path("catalog/packages/", public_views.catalog_packages, name="booking-catalog-packages"),
    path("catalog/resolve/", public_views.catalog_resolve, name="booking-catalog-resolve"),
    path("catalog/resolve-handoff/", public_views.catalog_resolve_handoff, name="booking-catalog-resolve-handoff"),
    path("calendar/", public_views.booking_calendar, name="booking-calendar"),
    path("availability/", public_views.booking_availability, name="booking-availability"),
    path("holds/", public_views.booking_hold_create, name="booking-hold-create"),
    path("checkout/", public_views.booking_checkout_create, name="booking-checkout-create"),
    path("policy-acceptance-text/", public_views.booking_policy_acceptance_text, name="booking-policy-acceptance-text"),
    path("status/<str:public_booking_id>/", booking_status, name="booking-status"),
]
