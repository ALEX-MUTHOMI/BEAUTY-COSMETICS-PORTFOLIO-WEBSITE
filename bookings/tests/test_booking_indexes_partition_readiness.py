import pytest

from bookings.models import Booking, BookingDayState, BookingServiceItem, FullPackage, Service, ServiceCategory


@pytest.mark.django_db
def test_booking_indexes_and_partition_readiness_fields_exist():
    booking_index_names = {index.name for index in Booking._meta.indexes}
    assert "bookings_local_date_status_idx" in booking_index_names
    assert "bookings_type_local_status_idx" in booking_index_names
    assert "bookings_resource_range_idx" in booking_index_names
    assert Booking._meta.get_field("local_booking_date")

    assert {index.name for index in BookingDayState._meta.indexes} >= {"booking_day_state_date_idx"}
    assert {index.name for index in BookingServiceItem._meta.indexes} >= {"booking_item_booking_idx"}
    assert {index.name for index in FullPackage._meta.indexes} >= {"full_package_slug_active_idx"}
    assert {index.name for index in ServiceCategory._meta.indexes} >= {"service_category_slug_active_idx"}
    assert {index.name for index in Service._meta.indexes} >= {"booking_service_catalog_idx"}
