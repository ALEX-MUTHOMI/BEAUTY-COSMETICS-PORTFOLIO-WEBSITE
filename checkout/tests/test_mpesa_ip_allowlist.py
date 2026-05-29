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


@pytest.mark.django_db
def test_sandbox_tunnel_callback_host_can_bypass_safaricom_cidr_only_in_sandbox(settings):
    settings.DARAJA_ENV = "sandbox"
    settings.DARAJA_CALLBACK_URL = "https://beauty-checkout.trycloudflare.com/api/checkout/mpesa/webhook/"
    settings.DARAJA_SANDBOX_CALLBACK_TUNNEL_DOMAINS = ["trycloudflare.com", "ngrok-free.app", "ngrok.io"]
    settings.SAFARICOM_ALLOWED_CIDRS = ["196.201.214.0/24"]
    client = APIClient()

    response = client.post(
        "/api/checkout/mpesa/webhook/",
        {"bad": "payload"},
        format="json",
        REMOTE_ADDR="203.0.113.5",
        HTTP_HOST="beauty-checkout.trycloudflare.com",
        HTTP_X_FORWARDED_PROTO="https",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_sandbox_tunnel_callback_bypass_is_not_available_in_production(settings):
    settings.DARAJA_ENV = "production"
    settings.DARAJA_CALLBACK_URL = "https://beauty-checkout.trycloudflare.com/api/checkout/mpesa/webhook/"
    settings.DARAJA_SANDBOX_CALLBACK_TUNNEL_DOMAINS = ["trycloudflare.com", "ngrok-free.app", "ngrok.io"]
    settings.SAFARICOM_ALLOWED_CIDRS = ["196.201.214.0/24"]
    client = APIClient()

    response = client.post(
        "/api/checkout/mpesa/webhook/",
        {"bad": "payload"},
        format="json",
        REMOTE_ADDR="203.0.113.5",
        HTTP_HOST="beauty-checkout.trycloudflare.com",
        HTTP_X_FORWARDED_PROTO="https",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_sandbox_tunnel_callback_bypass_requires_configured_host_match(settings):
    settings.DARAJA_ENV = "sandbox"
    settings.DARAJA_CALLBACK_URL = "https://beauty-checkout.trycloudflare.com/api/checkout/mpesa/webhook/"
    settings.DARAJA_SANDBOX_CALLBACK_TUNNEL_DOMAINS = ["trycloudflare.com", "ngrok-free.app", "ngrok.io"]
    settings.SAFARICOM_ALLOWED_CIDRS = ["196.201.214.0/24"]
    client = APIClient()

    response = client.post(
        "/api/checkout/mpesa/webhook/",
        {"bad": "payload"},
        format="json",
        REMOTE_ADDR="203.0.113.5",
        HTTP_HOST="attacker.trycloudflare.com",
        HTTP_X_FORWARDED_PROTO="https",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
