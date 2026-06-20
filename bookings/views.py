import uuid

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from bookings.selectors.booking_status import email_status as _email_status  # noqa: F401
from bookings.selectors.booking_status import get_public_booking_for_status
from bookings.selectors.booking_status import next_action as _next_action  # noqa: F401
from bookings.selectors.booking_status import payment_status as _payment_status  # noqa: F401
from bookings.selectors.booking_status import receipt_status as _receipt_status  # noqa: F401
from bookings.selectors.booking_status import reminder_status as _reminder_status  # noqa: F401
from bookings.selectors.booking_status import reschedule_payload as _reschedule_payload  # noqa: F401
from bookings.selectors.booking_status import status_payload as _status_payload
from core.throttling import route_throttle

GENERIC_STATUS_UNAVAILABLE = {"detail": "Booking status is unavailable."}


def _generic_404():
    response = JsonResponse(GENERIC_STATUS_UNAVAILABLE, status=404)
    _apply_no_store_headers(response)
    return response


def _apply_no_store_headers(response):
    response["Cache-Control"] = "no-store"
    response["Pragma"] = "no-cache"
    response["X-Content-Type-Options"] = "nosniff"


@require_GET
@route_throttle("booking_status")
def booking_status(request, public_booking_id):
    try:
        public_id = uuid.UUID(str(public_booking_id))
    except (TypeError, ValueError):
        return _generic_404()

    booking = get_public_booking_for_status(public_id)
    if booking is None:
        return _generic_404()

    response = JsonResponse(_status_payload(booking))
    _apply_no_store_headers(response)
    return response
