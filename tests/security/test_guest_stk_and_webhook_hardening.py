"""Red-team proofs: guest STK bind + webhook shared secret fail-closed."""

import json

import pytest
from django.test import Client
from rest_framework import status
from rest_framework.test import APIClient

from bookings.models import Booking
from bookings.privacy import decrypt_value
from bookings.services.holds import BookingHoldService
from bookings.tests.factories import create_service_resource_customer
from bookings.tests.test_booking_checkout_contract import (
    _contract_service,
    _held_booking,
    _starts,
    accepted_policy_context,
)
from checkout.models import CheckoutAttempt, CheckoutSession
from checkout.webhook_auth import webhook_shared_secret_required


def _held_with_contact(*, email, phone, key):
    service, resource, _customer = create_service_resource_customer()
    result = BookingHoldService.create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=_starts(),
        customer_payload={"full_name": "Grace Wanjiku", "email": email, "phone": phone},
        idempotency_key=key,
    )
    return Booking.objects.get(public_id=result["booking_public_id"])


def _csrf_client():
    client = Client(enforce_csrf_checks=True)
    response = client.get("/api/csrf/", secure=True)
    assert response.status_code == 200
    return client, response.json()["csrf_token"]


def _post_json(client, path, payload, csrf_token):
    return client.post(
        path,
        data=json.dumps(payload),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf_token,
        HTTP_REFERER="https://testserver/",
        secure=True,
    )


@pytest.mark.django_db
def test_guest_stk_happy_path_bound_to_booking_phone():
    booking = _held_with_contact(
        email="guest-stk@aesthetic-os.test",
        phone="+254712345678",
        key="guest-stk-happy-hold",
    )
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="guest-stk-happy-1",
        request_context=accepted_policy_context(),
    )
    phone = decrypt_value(booking.customer_profile.phone_encrypted)
    client, csrf_token = _csrf_client()
    response = _post_json(
        client,
        "/api/bookings/checkout/mpesa/stk/",
        {
            "booking_public_id": str(booking.public_id),
            "checkout_public_id": checkout["checkout_public_id"],
            "phone_number": phone,
            "idempotency_key": "guest-stk-attempt-1",
        },
        csrf_token,
    )
    assert response.status_code == 202, response.content
    body = response.json()
    assert body["stk"]["next_action"] == "await_stk_confirmation"
    assert CheckoutAttempt.objects.filter(idempotency_key="guest-stk-attempt-1").exists()
    session = CheckoutSession.objects.get(id=checkout["checkout_public_id"])
    assert session.status == CheckoutSession.Status.STK_SENT


@pytest.mark.django_db
def test_guest_stk_rejects_attacker_phone_even_with_valid_ids():
    booking = _held_booking(key="guest-stk-phone-hold")
    checkout = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking.public_id,
        idempotency_key="guest-stk-phone-1",
        request_context=accepted_policy_context(),
    )
    client, csrf_token = _csrf_client()
    response = _post_json(
        client,
        "/api/bookings/checkout/mpesa/stk/",
        {
            "booking_public_id": str(booking.public_id),
            "checkout_public_id": checkout["checkout_public_id"],
            "phone_number": "+254700000099",
            "idempotency_key": "guest-stk-attempt-bad-phone",
        },
        csrf_token,
    )
    assert response.status_code == 400
    assert not CheckoutAttempt.objects.filter(idempotency_key="guest-stk-attempt-bad-phone").exists()


@pytest.mark.django_db
def test_guest_stk_rejects_cross_booking_checkout_bind():
    booking_a = _held_with_contact(
        email="guest-stk-a@aesthetic-os.test",
        phone="+254712345601",
        key="guest-stk-cross-a-hold",
    )
    booking_b = _held_with_contact(
        email="guest-stk-b@aesthetic-os.test",
        phone="+254712345602",
        key="guest-stk-cross-b-hold",
    )
    checkout_a = _contract_service().create_checkout_for_held_booking(
        booking_public_id=booking_a.public_id,
        idempotency_key="guest-stk-cross-a",
        request_context=accepted_policy_context(),
    )
    phone_b = decrypt_value(booking_b.customer_profile.phone_encrypted)
    client, csrf_token = _csrf_client()
    response = _post_json(
        client,
        "/api/bookings/checkout/mpesa/stk/",
        {
            "booking_public_id": str(booking_b.public_id),
            "checkout_public_id": checkout_a["checkout_public_id"],
            "phone_number": phone_b,
            "idempotency_key": "guest-stk-attempt-cross",
        },
        csrf_token,
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_webhook_shared_secret_required_in_live_mode(settings):
    settings.PAYMENT_PROVIDER_MODE = "daraja_live"
    settings.MPESA_WEBHOOK_SHARED_SECRET = ""
    settings.MPESA_WEBHOOK_REQUIRE_SHARED_SECRET = False
    assert webhook_shared_secret_required() is True


@pytest.mark.django_db
def test_webhook_rejects_missing_shared_secret_when_required(settings):
    settings.SAFARICOM_ALLOWED_CIDRS = ["127.0.0.1/32"]
    settings.MPESA_WEBHOOK_REQUIRE_SHARED_SECRET = True
    settings.MPESA_WEBHOOK_SHARED_SECRET = "super-secret-webhook-token-32chars!!"
    settings.PAYMENT_PROVIDER_MODE = "fake"
    client = APIClient()
    client.defaults["HTTP_X_FORWARDED_PROTO"] = "https"

    rejected = client.post(
        "/api/checkout/mpesa/webhook/",
        {
            "CheckoutRequestID": "ws-1",
            "MerchantRequestID": "m-1",
            "ResultCode": 0,
            "Amount": "100.00",
            "MpesaReceiptNumber": "ABC",
        },
        format="json",
        REMOTE_ADDR="127.0.0.1",
    )
    assert rejected.status_code == status.HTTP_403_FORBIDDEN

    accepted = client.post(
        "/api/checkout/mpesa/webhook/",
        {
            "CheckoutRequestID": "ws-2",
            "MerchantRequestID": "m-2",
            "ResultCode": 1,
        },
        format="json",
        REMOTE_ADDR="127.0.0.1",
        HTTP_X_AESTHETIC_OS_WEBHOOK_SECRET="super-secret-webhook-token-32chars!!",
    )
    assert accepted.status_code in {status.HTTP_202_ACCEPTED, status.HTTP_400_BAD_REQUEST}


@pytest.mark.django_db
def test_sandbox_tunnel_bypass_requires_explicit_allow_flag(settings):
    settings.DARAJA_ENV = "sandbox"
    settings.DEBUG = False
    settings.DARAJA_SANDBOX_ALLOW_TUNNEL_CALLBACKS = False
    settings.ALLOWED_HOSTS = ["aesthetic-os-checkout.trycloudflare.com"]
    settings.DARAJA_CALLBACK_URL = "https://aesthetic-os-checkout.trycloudflare.com/api/checkout/mpesa/webhook/"
    settings.DARAJA_SANDBOX_CALLBACK_TUNNEL_DOMAINS = ["trycloudflare.com"]
    settings.SAFARICOM_ALLOWED_CIDRS = ["196.201.214.0/24"]
    client = APIClient()
    response = client.post(
        "/api/checkout/mpesa/webhook/",
        {"bad": "payload"},
        format="json",
        REMOTE_ADDR="203.0.113.5",
        HTTP_HOST="aesthetic-os-checkout.trycloudflare.com",
        HTTP_X_FORWARDED_PROTO="https",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_celery_beat_schedule_registers_expiry_sweeps(settings):
    schedule = settings.CELERY_BEAT_SCHEDULE
    assert "sweep-stale-booking-holds" in schedule
    assert schedule["sweep-stale-booking-holds"]["task"] == "bookings.tasks.sweep_stale_holds"
    assert "sweep-expired-checkout-sessions" in schedule
    assert "sweep-booking-reminders" in schedule
    assert schedule["sweep-booking-reminders"]["task"] == "bookings.tasks.sweep_booking_reminders"
