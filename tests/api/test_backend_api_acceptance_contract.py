import json
from datetime import datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client
from django.utils import timezone

from bookings.models import BookableResource, BusinessHours, FullPackage, Service, ServiceCategory, ServiceSubcategory

NAIROBI = ZoneInfo("Africa/Nairobi")


def _csrf_client():
    client = Client(enforce_csrf_checks=True)
    response = client.get("/api/csrf/", secure=True)
    assert response.status_code == 200
    return client, response.json()["csrf_token"]


def _future_weekday(target):
    today = timezone.localdate()
    delta = (target - today.weekday()) % 7
    if delta == 0:
        delta = 7
    return today + timedelta(days=delta)


def _seed_catalog():
    category = ServiceCategory.objects.create(name="<b>Hair</b>", slug="api-hair", sort_order=1)
    subcategory = ServiceSubcategory.objects.create(category=category, name="Braids", slug="api-braids")
    service = Service.objects.create(
        name="<img src=x onerror=alert(1)> API Braids",
        slug="api-braids-service",
        category="legacy-hair",
        category_ref=category,
        subcategory=subcategory,
        duration_minutes=60,
        base_price=Decimal("2500.00"),
    )
    package = FullPackage.objects.create(
        name="API Bridal Package",
        slug="api-bridal-package",
        duration_minutes=240,
        price_amount=Decimal("12000.00"),
    )
    resource = BookableResource.objects.create(name="API Chair", resource_type=BookableResource.Type.CHAIR)
    BusinessHours.create_default_week(resource=resource)
    return service, package, resource


def _post_json(client, path, payload, csrf_token):
    return client.post(
        path,
        data=json.dumps(payload),
        content_type="application/json",
        secure=True,
        HTTP_X_CSRFTOKEN=csrf_token,
        HTTP_REFERER="https://testserver/api/csrf/",
    )


def _assert_no_sensitive_contract_keys(payload):
    rendered = json.dumps(payload, sort_keys=True).lower()
    forbidden = [
        "ledger_id",
        "checkout_session_id",
        "provider_payload",
        "raw_payload",
        "password",
        "otp",
        "token_hash",
        "session_key",
        "original_private_key",
        "quarantine_key",
        "storage_secret",
        "traceback",
        "/app/",
    ]
    for value in forbidden:
        assert value not in rendered


@pytest.mark.django_db
def test_api_health_alias_and_csrf_bootstrap_are_json_safe():
    client = Client(enforce_csrf_checks=True)

    health = client.get("/api/health-check/", secure=True)
    csrf = client.get("/api/csrf/", secure=True)

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert csrf.status_code == 200
    assert csrf.cookies.get("csrftoken")
    assert csrf.json()["csrf_token"]
    _assert_no_sensitive_contract_keys(csrf.json())


@pytest.mark.django_db
def test_public_catalog_availability_and_hold_contracts_are_safe():
    service, package, resource = _seed_catalog()
    client, csrf_token = _csrf_client()
    monday = _future_weekday(0)
    starts_at = datetime.combine(monday, time(9, 0), tzinfo=NAIROBI).isoformat()

    services = client.get("/api/bookings/catalog/services/", secure=True)
    packages = client.get("/api/bookings/catalog/packages/", secure=True)
    availability = client.get(
        "/api/bookings/availability/",
        {
            "selection_type": "normal",
            "service_public_id": str(service.id),
            "resource_public_id": str(resource.id),
            "start_date": monday.isoformat(),
            "end_date": monday.isoformat(),
        },
        secure=True,
    )
    missing_csrf = Client(enforce_csrf_checks=True).post(
        "/api/bookings/holds/",
        data="{}",
        content_type="application/json",
        secure=True,
    )
    hold = _post_json(
        client,
        "/api/bookings/holds/",
        {
            "selection_type": "normal",
            "service_public_id": str(service.id),
            "resource_public_id": str(resource.id),
            "starts_at": starts_at,
            "idempotency_key": "api-acceptance-hold-1",
            "customer": {
                "full_name": "Test Customer",
                "email": "test.customer@example.invalid",
                "phone": "+254700000000",
            },
        },
        csrf_token,
    )
    tampered = _post_json(
        client,
        "/api/bookings/holds/",
        {
            "selection_type": "normal",
            "service_public_id": str(service.id),
            "resource_public_id": str(resource.id),
            "starts_at": starts_at,
            "idempotency_key": "api-acceptance-hold-tampered",
            "amount": "1.00",
            "customer": {
                "full_name": "Test Customer",
                "email": "test.customer@example.invalid",
                "phone": "+254700000000",
            },
        },
        csrf_token,
    )
    package_availability = client.get(
        "/api/bookings/availability/",
        {
            "selection_type": "full_package",
            "full_package_public_id": str(package.public_id),
            "resource_public_id": str(resource.id),
            "start_date": _future_weekday(1).isoformat(),
            "end_date": _future_weekday(1).isoformat(),
        },
        secure=True,
    )

    assert services.status_code == 200
    assert packages.status_code == 200
    assert availability.status_code == 200
    assert availability.json()["availability"][0]["slots"]
    assert package_availability.status_code == 200
    assert missing_csrf.status_code == 403
    assert hold.status_code == 201
    assert hold.json()["booking"]["status"] == "held"
    assert tampered.status_code == 400
    for response in (services, packages, availability, package_availability, hold, tampered):
        _assert_no_sensitive_contract_keys(response.json())
    assert "<" not in json.dumps(services.json())


@pytest.mark.django_db
def test_staff_auth_cookie_session_contract_uses_csrf_and_never_returns_session_key():
    User = get_user_model()
    user = User.objects.create_user(email="api.staff@example.invalid", password="LocalApiAcceptancePassphrase!2026")
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=["is_staff", "is_superuser", "updated_at"])
    user.user_permissions.add(*Permission.objects.filter(codename__startswith="view_staff"))
    client, csrf_token = _csrf_client()

    no_csrf = Client(enforce_csrf_checks=True).post(
        "/api/staff/auth/login/",
        data=json.dumps({"email": user.email, "password": "LocalApiAcceptancePassphrase!2026"}),
        content_type="application/json",
        secure=True,
    )
    login = _post_json(
        client,
        "/api/staff/auth/login/",
        {"email": user.email, "password": "LocalApiAcceptancePassphrase!2026"},
        csrf_token,
    )
    me = client.get("/api/staff/auth/me/", secure=True)

    assert no_csrf.status_code == 403
    assert login.status_code == 200
    assert client.cookies.get("sessionid")
    assert me.status_code == 200
    _assert_no_sensitive_contract_keys(login.json())
    _assert_no_sensitive_contract_keys(me.json())
