import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_malformed_webhook_from_allowed_ip_is_rejected_without_internal_detail(
    settings,
):
    settings.SAFARICOM_ALLOWED_CIDRS = ["127.0.0.1/32"]
    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

    response = client.post(
        "/api/checkout/mpesa/webhook/",
        {"unexpected": "payload"},
        format="json",
        REMOTE_ADDR="127.0.0.1",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "checkout" not in str(response.data).lower()
