import uuid

from django.db.models import Exists, OuterRef, Subquery
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from bookings.models import (
    Booking,
    BookingNotification,
    BookingReminder,
)
from bookings.selectors.booking_status import status_payload

# Compatibility re-exports: old private names used by existing tests.
# Canonical implementation lives in bookings.selectors.booking_status.
from bookings.selectors.booking_status import (  # noqa: F401
    email_status as _email_status,
    next_action as _next_action,
    payment_status as _payment_status,
    receipt_status as _receipt_status,
    reminder_status as _reminder_status,
    reschedule_payload as _reschedule_payload,
    status_payload as _status_payload,
)

GENERIC_STATUS_UNAVAILABLE = {"detail": "Booking status is unavailable."}


def _generic_404():
    return JsonResponse(GENERIC_STATUS_UNAVAILABLE, status=404)


@require_GET
def booking_status(request, public_booking_id):
    try:
        public_id = uuid.UUID(str(public_booking_id))
    except (TypeError, ValueError):
        return _generic_404()

    receipt_notification = BookingNotification.objects.filter(
        booking=OuterRef("pk"),
        notification_type="booking_confirmed_with_receipt",
    ).order_by("-created_at")
    reminder_qs = BookingReminder.objects.filter(booking=OuterRef("pk"))
    booking = (
        Booking.objects.select_related("service", "full_package", "receipt", "receipt__pdf_artifact")
        .annotate(
            _receipt_notification_status=Subquery(receipt_notification.values("status")[:1]),
            _has_pending_reminder=Exists(reminder_qs.filter(status=BookingReminder.Status.PENDING)),
            _has_sent_reminder=Exists(reminder_qs.filter(status=BookingReminder.Status.SENT)),
            _has_failed_reminder=Exists(
                reminder_qs.filter(
                    status__in=[
                        BookingReminder.Status.FAILED,
                        BookingReminder.Status.ADMIN_REVIEW_REQUIRED,
                    ]
                )
            ),
        )
        .filter(public_id=public_id)
        .first()
    )
    if booking is None:
        return _generic_404()

    response = JsonResponse(status_payload(booking))
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
