import re
import uuid
from datetime import date, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, Q
from django.utils import timezone

from billing.models import LedgerTransaction
from billing.redaction import hash_sensitive_value
from bookings.domain.day_policy import built_in_policy_for_weekday
from bookings.infrastructure.receipt_pdf import ReceiptPDFService
from bookings.models import (
    BOOKING_BLOCKING_STATUSES,
    Booking,
    BookingFinancialHistory,
    BookingNotification,
    BookingReminder,
    ReceiptPDFArtifact,
    StaffActionAuditEvent,
)
from bookings.privacy import decrypt_value, safe_display_name
from bookings.services.staff_roles import is_beautician, scope_bookings_queryset
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
        .select_related(
            "customer_profile",
            "service",
            "resource",
            "full_package",
            "assigned_staff",
            "assigned_staff__staff_profile",
        )
        .prefetch_related(
            "service_items",
            Prefetch("notifications", queryset=BookingNotification.objects.order_by("-created_at")),
            Prefetch("reminders", queryset=BookingReminder.objects.order_by("-created_at")),
        )
        .order_by("starts_at", "public_id")
    )


def _all_booking_queryset():
    return (
        Booking.objects.select_related(
            "customer_profile",
            "service",
            "resource",
            "full_package",
            "assigned_staff",
            "assigned_staff__staff_profile",
        )
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
    assigned = booking.assigned_staff
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
        "fulfillment_status": booking.fulfillment_status,
        "payment_status": _payment_status(booking),
        "receipt_status": _receipt_status(booking),
        "reminder_status": _reminder_status(booking),
        "notification_status": _notification_status(booking),
        "reschedule_status": "requested" if booking.status == Booking.Status.RESCHEDULE_REQUESTED else "none",
        "no_refund_policy_acknowledged": bool(booking.no_refund_policy_accepted_at),
        "created_at_eat": _eat_datetime(booking.created_at),
        "assigned_staff_id": assigned.pk if assigned else None,
        "assigned_staff_email": getattr(assigned, "email", None) if assigned else None,
        "assigned_staff_display_name": (
            _safe_text(getattr(getattr(assigned, "staff_profile", None), "display_name", None) or "")
            or (str(assigned.email).split("@", 1)[0] if assigned else None)
        ),
    }


def _apply_assigned_filter(bookings, *, staff_user=None, assigned_to=""):
    bookings = scope_bookings_queryset(bookings, staff_user) if staff_user is not None else bookings
    assigned_to = _safe_text(assigned_to or "", max_length=64).lower()
    if not assigned_to or staff_user is None:
        return bookings
    if is_beautician(staff_user):
        # Beauticians are forced to their own assignments regardless of query.
        return bookings.filter(assigned_staff_id=staff_user.pk)
    if assigned_to == "me":
        return bookings.filter(assigned_staff_id=staff_user.pk)
    if assigned_to == "unassigned":
        return bookings.filter(assigned_staff__isnull=True)
    # UUID or numeric staff id
    return bookings.filter(assigned_staff_id=assigned_to)


def get_daily_schedule(date_value, filters=None, *, staff_user=None):
    local_date = _parse_date(date_value)
    filters = filters or {}
    bookings = _base_booking_queryset().filter(local_booking_date=local_date)
    bookings = _apply_assigned_filter(
        bookings,
        staff_user=staff_user,
        assigned_to=filters.get("assigned_to", ""),
    )
    status = _safe_text(filters.get("status", ""), max_length=32)
    booking_type = _safe_text(filters.get("booking_type", ""), max_length=32)
    if status:
        bookings = bookings.filter(status=status)
    if booking_type in {Booking.BookingType.NORMAL, Booking.BookingType.URGENT, Booking.BookingType.FULL_PACKAGE}:
        bookings = bookings.filter(booking_type=booking_type)
    rows = [
        _appointment_row(booking)
        for booking in bookings.select_related("assigned_staff", "assigned_staff__staff_profile")[:500]
    ]
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


def get_booking_detail(public_booking_id, *, include_payment=False, staff_user=None):
    booking = _get_booking(public_booking_id)
    if staff_user is not None and is_beautician(staff_user) and booking.assigned_staff_id != staff_user.pk:
        raise StaffBookingNotFound
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


STAFF_RECEIPT_PDF_CACHE_TTL_SECONDS = 45


def _read_ready_receipt_artifact(receipt):
    existing = getattr(receipt, "pdf_artifact", None)
    if not existing:
        return None
    if existing.status != ReceiptPDFArtifact.Status.READY or existing.regeneratable:
        return None
    try:
        return ReceiptPDFService.read_artifact(existing)
    except ValidationError:
        return None


def get_staff_receipt_pdf(public_booking_id, *, staff_user, ip_address="", user_agent=""):
    """
    Return receipt PDF bytes for staff download.

    Prefer an existing READY artifact (Celery/local storage). If generation is
    required, use a short-lived cache so double-clicks do not double-render under
    Gunicorn. Missing receipts stay fail-closed as StaffBookingNotFound (404).
    """
    booking = _get_booking(public_booking_id)
    receipt = getattr(booking, "receipt", None)
    if not receipt:
        raise StaffBookingNotFound

    pdf = _read_ready_receipt_artifact(receipt)
    if pdf is None:
        cache_key = f"staff_receipt_pdf_bytes:{receipt.pk}"
        cached = cache.get(cache_key)
        if cached:
            pdf = cached
        else:
            try:
                pdf = ReceiptPDFService.ensure_artifact(receipt)
            except (ValidationError, TimeoutError, OSError):
                raise StaffBookingNotFound from None
            cache.set(cache_key, pdf, timeout=STAFF_RECEIPT_PDF_CACHE_TTL_SECONDS)

    StaffActionAuditEvent.objects.create(
        staff=staff_user,
        booking=booking,
        action=StaffActionAuditEvent.Action.RECEIPT_DOWNLOAD,
        reason="Staff viewed booking receipt PDF",
        metadata_redacted={
            "booking_reference": str(booking.public_id),
            "ip_hash": hash_sensitive_value(ip_address or "unknown"),
            "user_agent_hash": hash_sensitive_value(user_agent or "unknown"),
        },
    )
    filename = f"receipt-{booking.public_id}.pdf"
    return pdf, filename


ALLOWED_FULFILLMENT_STATUSES = {
    Booking.FulfillmentStatus.ATTENDED,
    Booking.FulfillmentStatus.IN_SERVICE,
    Booking.FulfillmentStatus.COMPLETED,
    Booking.FulfillmentStatus.NO_SHOW,
    Booking.FulfillmentStatus.NOT_STARTED,
}


def set_booking_fulfillment(public_booking_id, *, staff_user, fulfillment_status):
    """
    Update desk fulfillment only — never mutates financial Booking.status.
    Beauticians may not fulfill peers' bookings even if mis-granted confirm perm.
    """
    status = _safe_text(fulfillment_status, max_length=32)
    if status not in ALLOWED_FULFILLMENT_STATUSES:
        raise StaffPortalValidationError("Invalid fulfillment status.")
    booking = _get_booking(public_booking_id)
    if is_beautician(staff_user) and booking.assigned_staff_id != staff_user.pk:
        raise StaffBookingNotFound
    if booking.fulfillment_status == status:
        return _appointment_row(booking)
    booking.fulfillment_status = status
    booking.fulfillment_updated_at = timezone.now()
    booking.fulfillment_updated_by = staff_user
    booking.save(
        update_fields=[
            "fulfillment_status",
            "fulfillment_updated_at",
            "fulfillment_updated_by",
            "updated_at",
        ]
    )
    StaffActionAuditEvent.objects.create(
        staff=staff_user,
        booking=booking,
        action=StaffActionAuditEvent.Action.ATTENDANCE_CONFIRM,
        reason=f"Fulfillment set to {status}",
        metadata_redacted={
            "booking_reference": str(booking.public_id),
            "fulfillment_status": status,
        },
    )
    return _appointment_row(booking)


def assign_booking_staff(public_booking_id, *, staff_user, assigned_staff_id=None):
    booking = _get_booking(public_booking_id)
    User = get_user_model()
    assignee = None
    if assigned_staff_id is not None and str(assigned_staff_id).strip() != "":
        assignee = User.objects.filter(pk=assigned_staff_id, is_staff=True, is_active=True).first()
        if not assignee:
            raise StaffPortalValidationError("Assigned staff is unavailable.")
    booking.assigned_staff = assignee
    booking.save(update_fields=["assigned_staff", "updated_at"])
    StaffActionAuditEvent.objects.create(
        staff=staff_user,
        booking=booking,
        action=StaffActionAuditEvent.Action.STAFF_ASSIGN,
        reason="Staff assignment updated",
        metadata_redacted={
            "booking_reference": str(booking.public_id),
            "assigned_staff_id": str(assignee.pk) if assignee else None,
        },
    )
    return _appointment_row(booking)


def staff_reschedule_booking(public_booking_id, *, staff_user, requested_starts_at, reason=""):
    """Staff desk move — wraps domain reschedule without customer OTP."""
    from django.utils.dateparse import parse_datetime

    from bookings.services.rescheduling import BookingRescheduleService

    booking = _get_booking(public_booking_id)
    if is_beautician(staff_user) and booking.assigned_staff_id != staff_user.pk:
        raise StaffBookingNotFound

    starts = requested_starts_at
    if isinstance(starts, str):
        starts = parse_datetime(starts)
    if starts is None:
        raise StaffPortalValidationError("Choose a valid new start time.")
    if timezone.is_naive(starts):
        starts = timezone.make_aware(starts, EAT)

    try:
        BookingRescheduleService.staff_reschedule(
            booking_public_id=str(booking.public_id),
            requested_starts_at=starts,
            reason=_safe_text(reason, max_length=255),
            actor_user=staff_user,
        )
    except ValidationError as exc:
        raise StaffPortalValidationError("Unable to reschedule booking.") from exc

    refreshed = _get_booking(public_booking_id)
    StaffActionAuditEvent.objects.create(
        staff=staff_user,
        booking=refreshed,
        action=StaffActionAuditEvent.Action.ATTENDANCE_CONFIRM,
        reason="Staff rescheduled booking",
        metadata_redacted={
            "booking_reference": str(refreshed.public_id),
            "new_local_date": refreshed.local_booking_date.isoformat() if refreshed.local_booking_date else "",
            "new_start_eat": _eat_time(refreshed.starts_at),
        },
    )
    return _appointment_row(refreshed)


def list_open_reschedule_queue(*, staff_user, days=7):
    """Open customer move requests (any future day) + confirmed visits in the near window."""
    today = timezone.now().astimezone(EAT).date()
    end = today + timedelta(days=max(1, min(int(days), MAX_STAFF_RANGE_DAYS)))
    # RESCHEDULE_REQUESTED is outside BOOKING_BLOCKING_STATUSES, so query via
    # _all_booking_queryset for open move requests; confirmed stays on the blocking set.
    scoped_all = scope_bookings_queryset(_all_booking_queryset(), staff_user)
    scoped = scope_bookings_queryset(_base_booking_queryset(), staff_user)
    # Requested moves should not fall off the desk after 7 days.
    open_moves = scoped_all.filter(
        status=Booking.Status.RESCHEDULE_REQUESTED,
        local_booking_date__gte=today,
    ).order_by(
        "starts_at"
    )[:50]
    movable = scoped.filter(
        status=Booking.Status.CONFIRMED,
        local_booking_date__gte=today,
        local_booking_date__lte=end,
    ).order_by("starts_at")[:40]
    seen = set()
    rows = []
    for booking in list(open_moves) + list(movable):
        key = str(booking.public_id)
        if key in seen:
            continue
        seen.add(key)
        row = _appointment_row(booking)
        row["local_date"] = booking.local_booking_date.isoformat() if booking.local_booking_date else ""
        row["queue_kind"] = "requested" if booking.status == Booking.Status.RESCHEDULE_REQUESTED else "confirmed"
        rows.append(row)
    return {"count": len(rows), "appointments": rows}


STAFF_SEARCH_MIN_QUERY_LENGTH = 3


def search_staff_bookings(q, *, staff_user, limit=50):
    query = _safe_text(q, max_length=80)
    if len(query) < STAFF_SEARCH_MIN_QUERY_LENGTH:
        raise StaffPortalValidationError("Search query must be at least 3 characters.")
    bookings = scope_bookings_queryset(_all_booking_queryset(), staff_user)
    filters = Q(customer_profile__full_name_display__icontains=query)
    try:
        parsed = uuid.UUID(query)
        filters |= Q(public_id=parsed)
    except ValueError:
        filters |= Q(public_id__icontains=query)
    # Receipt / provider refs live on related receipt when present.
    filters |= Q(receipt__receipt_number__icontains=query)
    rows = [
        _appointment_row(booking)
        for booking in bookings.filter(filters).distinct()[: max(1, min(int(limit or 50), 100))]
    ]
    return {"query": query, "count": len(rows), "appointments": rows}


def list_assignable_beauticians(limit=20):
    """Return active staff with beautician role for assignment UI (max ~10 expected)."""
    from bookings.models import StaffProfile

    profiles = (
        StaffProfile.objects.select_related("user")
        .filter(role=StaffProfile.Role.BEAUTICIAN, user__is_active=True, user__is_staff=True)
        .order_by("display_name", "user__email")[: max(1, min(int(limit or 20), 20))]
    )
    return [
        {
            "id": profile.user_id,
            "email": profile.user.email,
            "display_name": _safe_text(profile.display_name or profile.user.email.split("@", 1)[0]),
            "role": profile.role,
        }
        for profile in profiles
    ]
