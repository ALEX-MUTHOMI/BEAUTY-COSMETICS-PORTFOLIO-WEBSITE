import json
from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient

from bookings.models import Booking
from bookings.services.holds import BookingHoldService
from bookings.services.legal import POLICY_ACCEPTANCE_TEXT, ensure_default_legal_documents
from bookings.tests.factories import create_service_resource_customer
from checkout.models import CheckoutSession

User = get_user_model()
NAIROBI = ZoneInfo("Africa/Nairobi")


def _starts_at(hour=9):
    return datetime.combine(date(2026, 6, 8), time(hour, 0), tzinfo=NAIROBI)


def _held_booking(key="phase-3b-mass-assignment"):
    service, resource, _customer = create_service_resource_customer()
    result = BookingHoldService.create_hold(
        service_public_id=service.id,
        resource_public_id=resource.id,
        starts_at=_starts_at(),
        customer_payload={
            "full_name": "Grace Wanjiku",
            "email": "grace@example.com",
            "phone": "+254712345678",
        },
        idempotency_key=key,
    )
    return Booking.objects.get(public_id=result["booking_public_id"])


@pytest.mark.django_db
def test_booking_hold_rejects_client_price_mass_assignment():
    service, resource, _customer = create_service_resource_customer()
    payload = {
        "service_public_id": str(service.id),
        "resource_public_id": str(resource.id),
        "starts_at": _starts_at().isoformat(),
        "idempotency_key": "phase-3b-price-tamper",
        "customer": {"full_name": "A", "email": "a@example.com", "phone": "+254700330001"},
        "amount": "1.00",
        "currency": "USD",
        "total_amount": "1.00",
    }

    response = Client().post(
        "/api/bookings/holds/",
        data=json.dumps(payload),
        content_type="application/json",
        secure=True,
    )

    assert response.status_code == 400
    assert Booking.objects.count() == 0


@pytest.mark.django_db
def test_booking_hold_ignores_server_owned_status_and_role_fields():
    service, resource, _customer = create_service_resource_customer()
    payload = {
        "service_public_id": str(service.id),
        "resource_public_id": str(resource.id),
        "starts_at": _starts_at().isoformat(),
        "idempotency_key": "phase-3b-hold-server-owned-fields",
        "customer": {"full_name": "A", "email": "a@example.com", "phone": "+254700330001"},
        "status": Booking.Status.CONFIRMED,
        "booking_status": Booking.Status.CONFIRMED,
        "payment_status": "paid",
        "is_paid": True,
        "is_staff": True,
        "role": "admin",
        "customer_id": "attacker-selected-customer",
    }

    response = Client().post(
        "/api/bookings/holds/",
        data=json.dumps(payload),
        content_type="application/json",
        secure=True,
    )

    assert response.status_code == 201
    created = Booking.objects.get()
    assert created.status == Booking.Status.HELD
    assert not created.checkout_session_id
    body = response.content.decode("utf-8", errors="replace")
    assert "confirmed" not in body
    assert "paid" not in body
    assert "attacker-selected-customer" not in body


@pytest.mark.django_db
def test_checkout_session_create_derives_owner_from_authenticated_user_not_payload():
    owner = User.objects.create_user(email="phase-3b-owner@example.com", phone_number="+254700330002")
    attacker = User.objects.create_user(email="phase-3b-attacker@example.com", phone_number="+254700330003")
    client = APIClient()
    client.force_authenticate(user=attacker)

    response = client.post(
        "/api/checkout/sessions/",
        {
            "amount": "99.00",
            "currency": "KES",
            "description": "Mass assignment checkout",
            "purchasable_type": "booking_candidate",
            "purchasable_id": "candidate-1",
            "idempotency_key": "phase-3b-checkout-mass-assignment",
            "customer": str(owner.id),
            "customer_id": str(owner.id),
            "user_id": str(owner.id),
            "status": CheckoutSession.Status.PAID,
            "is_staff": True,
            "is_superuser": True,
            "provider_reference": "fake-provider-ref",
        },
        format="json",
        secure=True,
    )

    assert response.status_code == 201
    session = CheckoutSession.objects.get(id=response.data["id"])
    attacker.refresh_from_db()
    assert session.customer == attacker
    assert session.status == CheckoutSession.Status.CREATED
    assert session.amount_snapshot == Decimal("99.00")
    assert attacker.is_staff is False
    assert attacker.is_superuser is False


@pytest.mark.django_db
def test_booking_checkout_bridge_ignores_payment_truth_mass_assignment():
    ensure_default_legal_documents()
    booking = _held_booking("phase-3b-checkout-bridge")

    response = Client().post(
        "/api/bookings/checkout/",
        data=json.dumps(
            {
                "booking_public_id": str(booking.public_id),
                "idempotency_key": "phase-3b-checkout-bridge-key",
                "payment_status": "paid",
                "status": Booking.Status.CONFIRMED,
                "is_paid": True,
                "amount": "1.00",
                "currency": "USD",
                "provider_reference": "fake-provider-reference",
                "ledger_id": "fake-ledger-id",
                "policy_acceptance": {
                    "accepted": True,
                    "checkbox_text": POLICY_ACCEPTANCE_TEXT,
                    "locale": "en-KE",
                    "timezone_name": "Africa/Nairobi",
                    "country_hint": "KE",
                },
            }
        ),
        content_type="application/json",
        secure=True,
    )

    assert response.status_code == 201
    booking.refresh_from_db()
    session = CheckoutSession.objects.get(id=booking.checkout_session_id)
    assert booking.status == Booking.Status.PAYMENT_PENDING
    assert session.status == CheckoutSession.Status.PAYMENT_PENDING
    assert session.amount_snapshot == booking.total_price_snapshot
    body = response.content.decode("utf-8", errors="replace")
    assert "fake-provider-reference" not in body
    assert "fake-ledger-id" not in body
