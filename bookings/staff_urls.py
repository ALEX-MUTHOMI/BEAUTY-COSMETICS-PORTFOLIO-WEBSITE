from django.urls import path

from bookings import staff_views

urlpatterns = [
    path("bookings/schedule/", staff_views.staff_booking_schedule, name="staff-booking-schedule"),
    path("bookings/week/", staff_views.staff_booking_week, name="staff-booking-week"),
    path("bookings/<str:public_booking_id>/", staff_views.staff_booking_detail, name="staff-booking-detail"),
    path(
        "bookings/<str:public_booking_id>/payment/",
        staff_views.staff_booking_payment,
        name="staff-booking-payment",
    ),
    path(
        "bookings/<str:public_booking_id>/contact-access/",
        staff_views.staff_booking_contact_access,
        name="staff-booking-contact-access",
    ),
]
