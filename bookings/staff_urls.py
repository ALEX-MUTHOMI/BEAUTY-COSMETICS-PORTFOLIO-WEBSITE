from django.urls import path

from bookings import gallery_views, staff_auth_views, staff_views

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
    path("auth/apple/start/", staff_auth_views.staff_apple_start, name="staff-apple-start"),
    path("auth/google/callback/", staff_auth_views.staff_google_callback, name="staff-google-callback"),
    path("auth/apple/callback/", staff_auth_views.staff_apple_callback, name="staff-apple-callback"),
    path("auth/providers/", staff_auth_views.staff_oauth_providers, name="staff-oauth-providers"),
    path("bookings/schedule/", staff_views.staff_booking_schedule, name="staff-booking-schedule"),
    path("bookings/week/", staff_views.staff_booking_week, name="staff-booking-week"),
    path("bookings/search/", staff_views.staff_booking_search, name="staff-booking-search"),
    path(
        "bookings/assignable/",
        staff_views.staff_assignable_beauticians,
        name="staff-assignable-beauticians",
    ),
    path("bookings/<str:public_booking_id>/", staff_views.staff_booking_detail, name="staff-booking-detail"),
    path(
        "bookings/<str:public_booking_id>/payment/",
        staff_views.staff_booking_payment,
        name="staff-booking-payment",
    ),
    path(
        "bookings/<str:public_booking_id>/receipt.pdf",
        staff_views.staff_booking_receipt_pdf,
        name="staff-booking-receipt-pdf",
    ),
    path(
        "bookings/<str:public_booking_id>/fulfillment/",
        staff_views.staff_booking_fulfillment,
        name="staff-booking-fulfillment",
    ),
    path(
        "bookings/<str:public_booking_id>/assign/",
        staff_views.staff_booking_assign,
        name="staff-booking-assign",
    ),
    path(
        "bookings/<str:public_booking_id>/contact-access/",
        staff_views.staff_booking_contact_access,
        name="staff-booking-contact-access",
    ),
    path("gallery/categories/", gallery_views.staff_gallery_categories, name="staff-gallery-categories"),
    path("gallery/images/", gallery_views.staff_gallery_image_upload, name="staff-gallery-image-upload"),
]
