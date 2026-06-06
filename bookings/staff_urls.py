from django.urls import path

from bookings import staff_auth_views, staff_views

urlpatterns = [
    path("auth/login/", staff_auth_views.staff_login, name="staff-auth-login"),
    path("auth/logout/", staff_auth_views.staff_logout, name="staff-auth-logout"),
    path("auth/me/", staff_auth_views.staff_me, name="staff-auth-me"),
    path("auth/reauth/", staff_auth_views.staff_reauth, name="staff-auth-reauth"),
    path(
        "auth/password-reset/request/",
        staff_auth_views.staff_password_reset_request,
        name="staff-password-reset-request",
    ),
    path(
        "auth/password-reset/confirm/",
        staff_auth_views.staff_password_reset_confirm,
        name="staff-password-reset-confirm",
    ),
    path("auth/google/start/", staff_auth_views.staff_google_start, name="staff-google-start"),
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
