from datetime import timedelta

import pytest
from django.utils import timezone

from bookings.models import Booking, BookingAuditEvent
from bookings.services.state_machine import BookingStateError, transition_booking
from bookings.tests.factories import create_booking


@pytest.mark.django_db
def test_valid_transition_persists_and_creates_audit_event():
    booking = create_booking(status=Booking.Status.REQUESTED)

    transition_booking(booking, Booking.Status.HELD, actor_type="system", reason="hold created")

    booking.refresh_from_db()
    assert booking.status == Booking.Status.HELD
    assert BookingAuditEvent.objects.filter(
        booking=booking,
        old_status=Booking.Status.REQUESTED,
        new_status=Booking.Status.HELD,
    ).exists()


@pytest.mark.django_db
def test_invalid_terminal_transition_is_rejected():
    booking = create_booking(status=Booking.Status.EXPIRED)

    with pytest.raises(BookingStateError):
        transition_booking(booking, Booking.Status.CONFIRMED, actor_type="system")


@pytest.mark.django_db
def test_no_show_requires_grace_period():
    booking = create_booking(status=Booking.Status.CONFIRMED)
    booking.starts_at = timezone.now() - timedelta(minutes=10)
    booking.save()

    with pytest.raises(BookingStateError):
        transition_booking(booking, Booking.Status.NO_SHOW, actor_type="staff")

    booking.starts_at = timezone.now() - timedelta(minutes=45)
    booking.save()
    transition_booking(booking, Booking.Status.NO_SHOW, actor_type="staff")

    booking.refresh_from_db()
    assert booking.status == Booking.Status.NO_SHOW
