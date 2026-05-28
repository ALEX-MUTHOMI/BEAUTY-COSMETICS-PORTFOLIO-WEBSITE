import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_x_forwarded_for_spoofing_does_not_bypass_checkout_webhook_ip_allowlist(
    settings,
):
    settings.SAFARICOM_ALLOWED_CIDRS = ["196.201.214.0/24"]
    settings.TRUSTED_PROXY_CIDRS = []
    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

    response = client.post(
        "/api/checkout/mpesa/webhook/",
        {"CheckoutRequestID": "ws_CO_SPOOF_A2", "ResultCode": 0, "Amount": "100.00"},
        format="json",
        REMOTE_ADDR="203.0.113.10",
        HTTP_X_FORWARDED_FOR="196.201.214.10",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
