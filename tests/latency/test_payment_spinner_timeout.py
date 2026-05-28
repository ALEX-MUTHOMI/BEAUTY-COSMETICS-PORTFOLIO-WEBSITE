from django.conf import settings


def test_checkout_spinner_and_polling_timeouts_are_bounded():
    assert 5 <= settings.PAYMENT_STK_CLIENT_TIMEOUT_SECONDS <= 60
    assert 2 <= settings.PAYMENT_STATUS_POLL_INTERVAL_SECONDS <= 15
    assert settings.PAYMENT_STATUS_MAX_WAIT_SECONDS <= 600
