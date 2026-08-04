from bookings.services.remember_device import REMEMBER_DEVICE_CUSTOMER_COPY


def test_remember_device_copy_does_not_call_profile_an_account():
    lower = REMEMBER_DEVICE_CUSTOMER_COPY.lower()
    assert "account" not in lower
    assert "password" not in lower
    assert "save my details on this device" in lower
