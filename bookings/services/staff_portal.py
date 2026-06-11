import re
import uuid
from datetime import date, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.db.models import Prefetch
from django.utils import timezone

from billing.models import LedgerTransaction
from billing.redaction import hash_sensitive_value
from bookings.domain.day_policy import built_in_policy_for_weekday
from bookings.models import (
    BOOKING_BLOCKING_STATUSES,
    Booking,
    BookingFinancialHistory,
    BookingNotification,
    BookingReminder,
    StaffActionAuditEvent,
)
from bookings.privacy import decrypt_value, safe_display_name
from checkout.models import CheckoutSession

EAT = ZoneInfo("Africa/Nairobi")
MAX_STAFF_RANGE_DAYS = 7


class StaffPortalError(Exception):
    pass


class StaffBookingNotFound(StaffPortalError):
    pass


class StaffPortalValidationError(StaffPortalError):
    pass


def _safe_text(value, *, max_length=128):
    value = re.sub(r"<[^>]*>", " ", str(value or ""))
    value = re.sub(r"(?i)\son[a-z]+\s*=\s*\S+", " ", value)
    value = re.sub(r"[\x00-\x1f\x7f]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:max_length]


def _parse_date(value, *, field_name="date"):
    try:
        return date.fromisoformat(str(value or ""))
    except ValueError as exc:
        raise StaffPortalValidationError(f"Invalid {field_name}.") from exc


def _day_policy(local_date):
    return built_in_policy_for_weekday(local_date.weekday())


def _day_type(local_date):
    policy = _day_policy(local_date)
    if policy.day_type == policy.DayType.CLOSED:
        return "closed"
    if policy.day_type == policy.DayType.FULL_PACKAGE:
        return "full_package"
    return "normal"


def _capacity_for_day(local_date, bookings=None):
    policy = _day_policy(local_date)
    max_clients = 0 if policy.day_type == policy.DayType.CLOSED else policy.max_clients
    if bookings is None:
        booked_clients = _base_booking_queryset().filter(local_booking_date=local_date).count()
    else:
        booked_clients = len(bookings)
    return {
        "max_clients": max_clients,
        "booked_clients": booked_clients,
        "remaining_clients": max(0, max_clients - booked_clients),
    }


def _base_booking_queryset():
    return (
        Booking.objects.filter(status__in=BOOKING_BLOCKING_STATUSES)
        .exclude(hold_expires_at__isnull=False, hold_expires_at__lte=timezone.now())
        .select_related("customer_profile", "service", "resource", "full_package")
        .prefetch_related(
            "service_items",
            Prefetch("notifications", queryset=BookingNotification.objects.order_by("-created_at")),
            Prefetch("reminders", queryset=BookingReminder.objects.order_by("-created_at")),
        )
        .order_by("starts_at", "public_id")
    )


def _all_booking_queryset():
    return (
        Booking.objects.select_related("customer_profile", "service", "resource", "full_package")
        .prefetch_related(
            "service_items",
            Prefetch("notifications", queryset=BookingNotification.objects.order_by("-created_at")),
            Prefetch("reminders", queryset=BookingReminder.objects.order_by("-created_at")),
        )
        .order_by("starts_at", "public_id")
    )


def _eat_time(value):
    if not value:
        return None
    return value.astimezone(EAT).strftime("%H:%M")


def _eat_datetime(value):
    if not value:
        return None
    return value.astimezone(EAT).isoformat()


def _booking_type(booking):
    if booking.booking_type == Booking.BookingType.FULL_PACKAGE or booking.full_package_id:
        return Booking.BookingType.FULL_PACKAGE
    if booking.service_items.count() > 1:
        return "bundle"
    return "single_service"


def _service_summary(booking):
    snapshot = booking.selection_snapshot_json_redacted or {}
    if booking.full_package_id:
        return _safe_text(snapshot.get("name") or booking.full_package.name)
    items = snapshot.get("items") if isinstance(snapshot, dict) else None
    if isinstance(items, list) and items:
        names = [_safe_text(item.get("name", ""), max_length=64) for item in items if isinstance(item, dict)]
        names = [name for name in names if name]
        if names:
            return ", ".join(names)[:160]
    if booking.service_id:
        return _safe_text(booking.service.name)
    return "Selected services"


def _receipt_status(booking):
    receipt = getattr(booking, "receipt", None)
    if not receipt:
        return "not_issued"
    return _safe_text(receipt.payment_status or "issued", max_length=32)


def _reminder_status(booking):
    reminders = list(getattr(booking, "_prefetched_objects_cache", {}).get("reminders", []))
    if not reminders:
        reminders = list(booking.reminders.order_by("-created_at")[:1])
    if not reminders:
        return "not_scheduled"
    return _safe_text(reminders[0].status, max_length=32)


def _notification_status(booking):
    notifications = list(getattr(booking, "_prefetched_objects_cache", {}).get("notifications", []))
    if not notifications:
        notifications = list(booking.notifications.order_by("-created_at")[:1])
    if not notifications:
        return "not_sent"
    return _safe_text(notifications[0].status, max_length=32)


def _payment_status(booking):
    if booking.status == Booking.Status.CONFIRMED:
        return "paid"
    if booking.status == Booking.Status.PAYMENT_FAILED:
        return "failed"
    if booking.status in {Booking.Status.HELD, Booking.Status.PAYMENT_PENDING}:
        return "payment_pending"
    return "not_paid"


def _appointment_row(booking):
    customer = booking.customer_profile
    return {
        "booking_reference": str(booking.public_id),
        "public_booking_id": str(booking.public_id),
        "start_time_eat": _eat_time(booking.starts_at),
        "end_time_eat": _eat_time(booking.ends_at),
        "duration_minutes": booking.total_duration_minutes,
        "booking_type": _booking_type(booking),
        "service_summary": _service_summary(booking),
        "customer_display_name_safe": safe_display_name(customer.full_name_display),
        "contact_redacted": {
            "phone": "available",
            "email": "available",
        },
        "booking_status": booking.status,
        "payment_status": _payment_status(booking),
        "receipt_status": _receipt_status(booking),
        "reminder_status": _reminder_status(booking),
        "notification_status": _notification_status(booking),
        "reschedule_status": "requested" if booking.status == Booking.Status.RESCHEDULE_REQUESTED else "none",
        "no_refund_policy_acknowledged": bool(booking.no_refund_policy_accepted_at),
        "created_at_eat": _eat_datetime(booking.created_at),
    }


def get_daily_schedule(date_value, filters=None):
    local_date = _parse_date(date_value)
    filters = filters or {}
    bookings = _base_booking_queryset().filter(local_booking_date=local_date)
    status = _safe_text(filters.get("status", ""), max_length=32)
    booking_type = _safe_text(filters.get("booking_type", ""), max_length=32)
    if status:
        bookings = bookings.filter(status=status)
    if booking_type in {Booking.BookingType.NORMAL, Booking.BookingType.URGENT, Booking.BookingType.FULL_PACKAGE}:
        bookings = bookings.filter(booking_type=booking_type)
    rows = [_appointment_row(booking) for booking in bookings[:500]]
    return {
        "local_date": local_date.isoformat(),
        "timezone": "Africa/Nairobi",
        "day_type": _day_type(local_date),
        "capacity": _capacity_for_day(local_date, rows),
        "appointments": rows,
    }


def get_weekly_overview(start_date_value):
    start_date = _parse_date(start_date_value, field_name="start_date")
    end_date = start_date + timedelta(days=MAX_STAFF_RANGE_DAYS)
    bookings = list(
        _base_booking_queryset().filter(local_booking_date__gte=start_date, local_booking_date__lt=end_date)
    )
    bookings_by_date = {}
    for booking in bookings:
        bookings_by_date.setdefault(booking.local_booking_date, []).append(booking)
    days = []
    for offset in range(MAX_STAFF_RANGE_DAYS):
        current = start_date + timedelta(days=offset)
        day_bookings = bookings_by_date.get(current, [])
        payment_counts = {}
        status_counts = {}
        for booking in day_bookings:
            payment_counts[_payment_status(booking)] = payment_counts.get(_payment_status(booking), 0) + 1
            status_counts[booking.status] = status_counts.get(booking.status, 0) + 1
        days.append(
            {
                "local_date": current.isoformat(),
                "day_type": _day_type(current),
                "capacity": _capacity_for_day(current, day_bookings),
                "appointments_count": len(day_bookings),
                "payment_status_counts": payment_counts,
                "booking_status_counts": status_counts,
            }
        )
    return {"week_start": start_date.isoformat(), "timezone": "Africa/Nairobi", "days": days}


def _get_booking(public_booking_id):
    try:
        parsed = uuid.UUID(str(public_booking_id))
    except ValueError as exc:
        raise StaffBookingNotFound from exc
    booking = _all_booking_queryset().filter(public_id=parsed).first()
    if not booking:
        raise StaffBookingNotFound
    return booking


def get_booking_detail(public_booking_id, *, include_payment=False):
    booking = _get_booking(public_booking_id)
    payload = _appointment_row(booking)
    payload.update(
        {
            "local_date": booking.local_booking_date.isoformat() if booking.local_booking_date else None,
            "resource": _safe_text(booking.resource.name),
            "amount": str(booking.total_price_snapshot),
            "currency": booking.currency_snapshot,
            "no_refund_policy_version": _safe_text(booking.terms_version, max_length=32),
        }
    )
    if include_payment:
        payload["payment_summary"] = get_payment_summary_for_booking(booking)
    return payload


def _ledger_for_booking(booking):
    if not booking.checkout_session_id:
        return None
    return (
        LedgerTransaction.objects.filter(external_correlation_id=booking.checkout_session_id)
        .order_by("-created_at")
        .first()
    )


def _checkout_for_booking(booking):
    if not booking.checkout_session_id:
        return None
    return CheckoutSession.objects.filter(id=str(booking.checkout_session_id)).first()


def get_payment_summary(public_booking_id):
    booking = _get_booking(public_booking_id)
    return get_payment_summary_for_booking(booking)


def get_payment_summary_for_booking(booking):
    ledger = _ledger_for_booking(booking)
    checkout = _checkout_for_booking(booking)
    history = BookingFinancialHistory.objects.filter(booking=booking).order_by("-occurred_at").first()
    amount = ledger.amount if ledger else booking.total_price_snapshot
    currency = ledger.currency if ledger else booking.currency_snapshot
    return {
        "payment_status": _payment_status(booking),
        "amount": str(amount.quantize(Decimal("0.01"))),
        "currency": currency,
        "ledger_status": ledger.status if ledger else "not_recorded",
        "checkout_status": checkout.status if checkout else "not_linked",
        "provider": ledger.provider if ledger else "mpesa",
        "provider_reference": "redacted" if ledger and ledger.provider_reference_hash else "unavailable",
        "receipt_status": _receipt_status(booking),
        "financial_history_event": history.event_type if history else "not_recorded",
        "paid_at_eat": _eat_datetime(ledger.credited_at) if ledger else None,
        "refund_action_available": False,
    }


def reveal_contact(public_booking_id, *, staff_user, reason, ip_address="", user_agent=""):
    reason = _safe_text(reason, max_length=255)
    if not reason:
        raise StaffPortalValidationError("Contact access reason is required.")
    booking = _get_booking(public_booking_id)
    metadata = {
        "booking_reference": str(booking.public_id),
        "reason_hash": hash_sensitive_value(reason),
        "ip_hash": hash_sensitive_value(ip_address or "unknown"),
        "user_agent_hash": hash_sensitive_value(user_agent or "unknown"),
    }
    StaffActionAuditEvent.objects.create(
        staff=staff_user,
        booking=booking,
        action=StaffActionAuditEvent.Action.CONTACT_REVEAL,
        reason=reason,
        metadata_redacted=metadata,
    )
    return {
        "customer_display_name_safe": safe_display_name(booking.customer_profile.full_name_display),
        "phone": decrypt_value(booking.customer_profile.phone_encrypted),
        "email": decrypt_value(booking.customer_profile.email_encrypted),
    }
