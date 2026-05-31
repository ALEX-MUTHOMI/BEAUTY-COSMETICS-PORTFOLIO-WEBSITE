import importlib
from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from bookings.models import Booking
from bookings.tests.factories import create_booking


@pytest.mark.django_db
def test_btree_gist_extension_migration_exists():
    migration = importlib.import_module("bookings.migrations.0004_btree_gist_booking_foundation")
    operation_names = {operation.__class__.__name__ for operation in migration.Migration.operations}
    assert "BtreeGistExtension" in operation_names


@pytest.mark.django_db(transaction=True)
def test_same_resource_overlap_rejected_but_adjacent_allowed():
    starts = timezone.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=2)
    first = create_booking(starts_at=starts, ends_at=starts + timedelta(hours=1), status=Booking.Status.HELD)

    create_booking(
        resource=first.resource,
        starts_at=starts + timedelta(hours=1),
        ends_at=starts + timedelta(hours=2),
        status=Booking.Status.HELD,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            create_booking(
                resource=first.resource,
                starts_at=starts + timedelta(minutes=30),
                ends_at=starts + timedelta(minutes=90),
                status=Booking.Status.HELD,
            )


@pytest.mark.django_db(transaction=True)
def test_non_blocking_statuses_and_different_resources_do_not_collide():
    starts = timezone.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=3)
    first = create_booking(starts_at=starts, ends_at=starts + timedelta(hours=1), status=Booking.Status.EXPIRED)

    create_booking(
        resource=first.resource,
        starts_at=starts + timedelta(minutes=15),
        ends_at=starts + timedelta(minutes=45),
        status=Booking.Status.HELD,
    )

    blocking = create_booking(starts_at=starts + timedelta(days=1), ends_at=starts + timedelta(days=1, hours=1))
    create_booking(
        starts_at=blocking.starts_at,
        ends_at=blocking.ends_at,
        status=Booking.Status.HELD,
    )
