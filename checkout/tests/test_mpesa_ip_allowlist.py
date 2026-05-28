import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_mpesa_webhook_rejects_non_safaricom_ip_and_accepts_allowed_test_ip(settings):
    settings.SAFARICOM_ALLOWED_CIDRS = ["127.0.0.1/32"]
    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

    rejected = client.post(
        "/api/checkout/mpesa/webhook/",
        {"bad": "payload"},
        format="json",
        REMOTE_ADDR="203.0.113.5",
    )
    accepted = client.post(
        "/api/checkout/mpesa/webhook/",
        {"bad": "payload"},
        format="json",
        REMOTE_ADDR="127.0.0.1",
    )

    assert rejected.status_code == status.HTTP_403_FORBIDDEN
    assert accepted.status_code in {
        status.HTTP_202_ACCEPTED,
        status.HTTP_400_BAD_REQUEST,
    }
