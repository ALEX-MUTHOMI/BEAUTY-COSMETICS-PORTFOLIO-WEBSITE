from datetime import date, datetime, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from bookings.models import Booking

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="booking-unit@beauty.com", phone_number="+254712000001"
    )


@pytest.mark.django_db
def test_booking_model_saves_with_expected_defaults(user):
    booking = Booking.objects.create(
        user=user,
        service_date=date(2026, 7, 1),
        time_slot="09:00",
    )

    assert booking.id
    assert booking.status == Booking.Status.PENDING_PAYMENT
    assert booking.service_name == "Beauty consultation"
    assert booking.beautician_payout_phone == "+254700000000"
    assert booking.ledger_transaction is None


@pytest.mark.django_db
def test_booking_calculates_duration_boundaries(user):
    booking = Booking.objects.create(
        user=user,
        service_date=date(2026, 7, 2),
        time_slot="13:30",
        duration_minutes=90,
    )

    assert booking.duration == timedelta(minutes=90)
    assert booking.starts_at == datetime(2026, 7, 2, 13, 30)
    assert booking.ends_at == datetime(2026, 7, 2, 15, 0)


@pytest.mark.django_db(transaction=True)
def test_booking_unique_service_date_time_slot_enforced_in_isolation(user):
    Booking.objects.create(
        user=user,
        service_date=date(2026, 7, 3),
        time_slot="11:00",
    )

    with pytest.raises(IntegrityError):
        Booking.objects.create(
            user=user,
            service_date=date(2026, 7, 3),
            time_slot="11:00",
        )
