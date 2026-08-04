from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError

from bookings.tests.factories import create_service_resource_customer

NAIROBI = ZoneInfo("Africa/Nairobi")


def _service():
    try:
        from bookings.services.availability import AvailabilityService
    except ImportError as exc:
        pytest.fail(f"AvailabilityService missing: {exc}")
    return AvailabilityService


@pytest.mark.django_db
def test_naive_datetime_input_is_rejected():
    service, resource, _customer = create_service_resource_customer()

    with pytest.raises(ValidationError):
        _service().get_available_slots(
            service.id,
            datetime(2026, 6, 1, 0, 0),
            datetime(2026, 6, 1, 23, 59),
            resource_id=resource.id,
        )


@pytest.mark.django_db
def test_nairobi_business_boundaries_convert_to_expected_utc_times():
    service, resource, _customer = create_service_resource_customer()
    monday = date(2026, 6, 1)

    result = _service().get_available_slots(service.id, monday, monday, resource_id=resource.id)

    first = datetime.fromisoformat(result[0]["slots"][0]["starts_at"])
    last_end = datetime.fromisoformat(result[0]["slots"][-1]["ends_at"])
    assert first.utcoffset() == NAIROBI.utcoffset(first)
    assert first.astimezone(ZoneInfo("UTC")).hour == 4
    assert last_end.astimezone(ZoneInfo("UTC")).hour == 16
    assert settings.USE_TZ is True


@pytest.mark.django_db
def test_returned_slots_are_explicitly_nairobi_offset():
    service, resource, _customer = create_service_resource_customer()
    monday = date(2026, 6, 1)

    result = _service().get_available_slots(service.id, monday, monday, resource_id=resource.id)

    assert result[0]["timezone"] == "Africa/Nairobi"
    assert result[0]["slots"][0]["starts_at"].endswith("+03:00")
