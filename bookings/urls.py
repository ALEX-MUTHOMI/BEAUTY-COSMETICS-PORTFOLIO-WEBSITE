from django.urls import path

from bookings.views import booking_status

urlpatterns = [
    path("status/<str:public_booking_id>/", booking_status, name="booking-status"),
]
