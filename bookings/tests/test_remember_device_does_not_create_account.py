import pytest

from bookings.tests.test_remember_device_helpers import confirmed_booking, remember_device


@pytest.mark.django_db
def test_remember_device_flow_does_not_create_customer_account_or_password(client, django_user_model):
    booking = confirmed_booking(key="remember-no-account")
    before = django_user_model.objects.count()

    remember_device(client, booking)

    assert django_user_model.objects.count() == before
