import pytest
from django.contrib.auth.models import Permission
from django.test import Client, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from bookings.tests.factories import create_booking
from bookings.tests.test_staff_portal_helpers import make_staff_user, staff_booking_url


def _assert_no_sensitive_markers(response, markers):
    body = response.content.decode("utf-8", errors="replace") if hasattr(response, "content") else str(response.data)
    for marker in markers:
        assert marker
        assert marker not in body


@pytest.mark.django_db
@override_settings(SAFARICOM_ALLOWED_CIDRS=["127.0.0.1/32"], TRUSTED_PROXY_CIDRS=[])
def test_disabled_legacy_billing_webhook_returns_410_after_ip_allowlist_accepts_request():
    response = APIClient().post(
        "/api/billing/mpesa-webhook/",
        {
            "CheckoutRequestID": "attacker-checkout-request-id",
            "MerchantRequestID": "attacker-merchant-request-id",
            "MpesaReceiptNumber": "attacker-receipt",
            "ResultCode": 0,
            "Amount": "1.00",
            "raw_payload": {"attempt": "should-not-be-reflected"},
        },
        format="json",
        secure=True,
        REMOTE_ADDR="127.0.0.1",
    )

    assert response.status_code == status.HTTP_410_GONE
    rendered = str(response.data)
    for marker in (
        "attacker-checkout-request-id",
        "attacker-merchant-request-id",
        "attacker-receipt",
        "raw_payload",
        "ledger",
    ):
        assert marker not in rendered


@pytest.mark.django_db
def test_staff_booking_access_policy_is_global_for_authorized_staff_and_denies_without_permission():
    booking_a = create_booking(idempotency_key="phase-3bc-staff-policy-a")
    booking_b = create_booking(idempotency_key="phase-3bc-staff-policy-b")
    authorized_staff = make_staff_user(permissions=["view_staff_booking"])
    unauthorized_staff = make_staff_user()
    unauthorized_staff.user_permissions.add(Permission.objects.get(codename="view_staff_portal"))

    authorized_client = Client()
    authorized_client.force_login(authorized_staff)
    session = authorized_client.session
    session["staff_auth_at"] = session["staff_last_activity_at"] = 4102444800.0
    session.save()

    unauthorized_client = Client()
    unauthorized_client.force_login(unauthorized_staff)
    session = unauthorized_client.session
    session["staff_auth_at"] = session["staff_last_activity_at"] = 4102444800.0
    session.save()

    first = authorized_client.get(staff_booking_url(booking_a), secure=True)
    second = authorized_client.get(staff_booking_url(booking_b), secure=True)
    denied = unauthorized_client.get(staff_booking_url(booking_a), secure=True)

    assert first.status_code == 200
    assert second.status_code == 200
    assert denied.status_code == 403
    _assert_no_sensitive_markers(denied, ["grace@example.com", "+254712345678", "phone", "email"])


@pytest.mark.django_db
def test_unknown_sensitive_api_route_fails_closed_without_debug_or_object_data():
    response = Client().get(
        "/api/checkout/sessions/00000000-0000-4000-8000-000000000000/private-ledger/?scope=all",
        secure=True,
    )

    assert response.status_code == 404
    _assert_no_sensitive_markers(
        response,
        [
            "Traceback",
            "Internal Server Error",
            "checkout_request_id",
            "ledger_id",
            "provider_reference",
            "raw_payload",
        ],
    )
