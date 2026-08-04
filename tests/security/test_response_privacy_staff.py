import pytest
from django.contrib.auth.models import Permission
from django.test import Client

from bookings.tests.factories import create_booking
from bookings.tests.test_staff_portal_helpers import (
    staff_booking_url,
    staff_contact_url,
    staff_login,
    staff_payment_url,
)
from tests.security.response_privacy_helpers import (
    AUTH_KEY_MARKERS,
    INTERNAL_DEBUG_KEY_MARKERS,
    KNOWN_TEST_PII_VALUES,
    PAYMENT_PROVIDER_KEY_MARKERS,
    STORAGE_KEY_MARKERS,
    assert_response_excludes_categories,
)


@pytest.mark.django_db
def test_staff_booking_detail_response_exposes_operational_fields_without_financial_or_auth_internals():
    booking = create_booking()
    client = Client()
    staff_login(client, permissions=["view_staff_booking"])

    response = client.get(staff_booking_url(booking), secure=True)

    assert response.status_code == 200
    payload = assert_response_excludes_categories(
        response,
        categories=(AUTH_KEY_MARKERS, STORAGE_KEY_MARKERS, INTERNAL_DEBUG_KEY_MARKERS),
        forbidden_values=KNOWN_TEST_PII_VALUES,
    )
    assert set(payload).issuperset(
        {
            "booking_reference",
            "public_booking_id",
            "booking_status",
            "payment_status",
            "contact_redacted",
        }
    )
    rendered = response.content.decode("utf-8")
    assert "provider_reference_hash" not in rendered
    assert "raw_payload" not in rendered
    assert "ledger_id" not in rendered


@pytest.mark.django_db
def test_staff_payment_summary_response_is_redacted_and_does_not_expose_provider_identifiers():
    booking = create_booking()
    client = Client()
    staff_login(client, permissions=["view_staff_payment_summary"])

    response = client.get(staff_payment_url(booking), secure=True)

    assert response.status_code == 200
    payload = assert_response_excludes_categories(
        response,
        categories=(AUTH_KEY_MARKERS, STORAGE_KEY_MARKERS, INTERNAL_DEBUG_KEY_MARKERS),
        forbidden_values=KNOWN_TEST_PII_VALUES | {str(booking.id)},
    )
    assert set(payload).issubset(
        {
            "payment_status",
            "amount",
            "currency",
            "ledger_status",
            "checkout_status",
            "provider",
            "provider_reference",
            "receipt_status",
            "financial_history_event",
            "paid_at_eat",
            "refund_action_available",
        }
    )
    assert payload["provider_reference"] in {"unavailable", "redacted"}


@pytest.mark.django_db
def test_staff_contact_reveal_success_allows_only_intended_contact_fields():
    booking = create_booking()
    client = Client()
    staff_login(client, permissions=["view_staff_contact_details"])

    response = client.post(staff_contact_url(booking), {"reason": "client arrival coordination"}, secure=True)

    assert response.status_code == 200
    payload = assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        allowed_keys={"phone", "email"},
    )
    assert set(payload).issubset({"customer_display_name_safe", "phone", "email"})


@pytest.mark.django_db
def test_staff_contact_reveal_denial_is_generic_and_contains_no_contact_data():
    booking = create_booking()
    client = Client()
    user = staff_login(client)
    user.user_permissions.add(Permission.objects.get(codename="view_staff_portal"))

    response = client.post(staff_contact_url(booking), {"reason": "probe"}, secure=True)

    assert response.status_code == 403
    assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        forbidden_values=KNOWN_TEST_PII_VALUES | {str(booking.public_id), str(booking.id)},
    )
