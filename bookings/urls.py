from django.urls import path

from bookings import api_views
from bookings.views import booking_status

urlpatterns = [
    path("catalog/services/", api_views.catalog_services, name="booking-catalog-services"),
    path("catalog/packages/", api_views.catalog_packages, name="booking-catalog-packages"),
    path("availability/", api_views.booking_availability, name="booking-availability"),
    path("holds/", api_views.booking_hold_create, name="booking-hold-create"),
    path("checkout/", api_views.booking_checkout_create, name="booking-checkout-create"),
    path("policy-acceptance-text/", api_views.booking_policy_acceptance_text, name="booking-policy-acceptance-text"),
    path("status/<str:public_booking_id>/", booking_status, name="booking-status"),
]
