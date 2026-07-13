"""
Hostile OWASP-mapped Red Team suite for Staff Portal boundaries.

Mapped:
  A07 Identification/Auth — brute force + CSRF bypass
  A01 Broken Access Control — vertical receipt + horizontal beautician BOLA
  A08 Integrity / mass assignment — fulfillment must not mutate money fields
  A03 Injection/DoS — search min-length + wildcard fuzz (no 500)

No happy-path coverage. Failures here are security regressions.
"""

import pytest
from django.test import Client

from bookings.infrastructure.receipt_pdf import ReceiptPDFService
from bookings.models import Booking, StaffProfile, StaffSecurityAudit
from bookings.services.staff_roles import apply_role_permissions
from bookings.tests.test_booking_checkout_contract import _held_booking
from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking
from bookings.tests.test_staff_auth_helpers import login_payload, make_staff
from bookings.tests.test_staff_portal_helpers import mark_confirmed, staff_login


@pytest.mark.django_db(transaction=True)
def test_a07_staff_login_brute_force_audits_and_throttles(settings):
    """15 invalid logins → login_failed audits + throttle (429), never 500."""
    settings.STAFF_LOGIN_FAILURE_LIMIT = 5
    settings.STAFF_LOGIN_FAILURE_WINDOW_SECONDS = 600
    settings.STAFF_LOGIN_COOLDOWN_SECONDS = 600
    make_staff(email="rt-brute@example.com")
    client = Client()
    statuses = []
    for _ in range(15):
        response = client.post(
            "/api/staff/auth/login/",
            login_payload(email="rt-brute@example.com", password="wrong password forever"),
            content_type="application/json",
            secure=True,
        )
        statuses.append(response.status_code)
        assert response.status_code in {400, 429}
        assert response.status_code != 500
        body = response.content.decode("utf-8", errors="ignore").lower()
        assert "password" not in body or "invalid credentials" in body or "try again" in body
        assert "traceback" not in body

    assert 429 in statuses
    failures = StaffSecurityAudit.objects.filter(event_type=StaffSecurityAudit.EventType.LOGIN_FAILURE)
    rate = StaffSecurityAudit.objects.filter(event_type=StaffSecurityAudit.EventType.LOGIN_RATE_LIMITED)
    assert failures.count() + rate.count() >= 5
    for event in list(failures[:5]) + list(rate[:3]):
        meta = event.metadata_redacted or {}
        serialized = str(meta).lower()
        assert "wrong password" not in serialized
        assert "correct horse" not in serialized
        assert meta.get("login_failed") is True or event.event_type == StaffSecurityAudit.EventType.LOGIN_RATE_LIMITED
        assert "reason" in meta


@pytest.mark.django_db(transaction=True)
def test_a07_staff_state_changing_post_rejects_missing_csrf():
    """Valid staff session without CSRF must not mutate fulfillment (403)."""
    booking = mark_confirmed(_held_booking(key="rt-csrf-fulfill"))
    prior_status = booking.status
    prior_fulfillment = booking.fulfillment_status

    client = Client(enforce_csrf_checks=True)
    staff_login(client, permissions=["confirm_staff_attendance", "view_staff_booking"])
    # Deliberately omit CSRF cookie/header — session alone must not authorize writes.
    response = client.post(
        f"/api/staff/bookings/{booking.public_id}/fulfillment/",
        data={"fulfillment_status": "completed"},
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 403
    booking.refresh_from_db()
    assert booking.status == prior_status
    assert booking.fulfillment_status == prior_fulfillment


@pytest.mark.django_db(transaction=True)
def test_a01_beautician_vertical_cannot_download_receipt(settings, tmp_path):
    """Beautician (no download_staff_receipt) → 403 on receipt.pdf."""
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("rt-vert-receipt")
    ReceiptPDFService.ensure_artifact(booking.receipt)

    client = Client()
    beautician = staff_login(
        client,
        permissions=["view_staff_portal", "view_staff_booking", "view_staff_payment_summary"],
    )
    apply_role_permissions(beautician, StaffProfile.Role.BEAUTICIAN)
    booking.assigned_staff = beautician
    booking.save(update_fields=["assigned_staff", "updated_at"])

    response = client.get(f"/api/staff/bookings/{booking.public_id}/receipt.pdf", secure=True)
    assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_a01_beautician_horizontal_bola_cannot_touch_peer_booking():
    """Beautician A cannot read or fulfill Beautician B's assignment (even if confirm mis-granted)."""
    from django.contrib.auth.models import Permission

    booking_b = mark_confirmed(_held_booking(key="rt-bola-b"))
    client_a = Client()
    beautician_a = staff_login(
        client_a,
        permissions=["view_staff_portal", "view_staff_booking", "view_staff_payment_summary"],
    )
    apply_role_permissions(beautician_a, StaffProfile.Role.BEAUTICIAN)
    # Hostile: ops mis-grants confirm on a scoped worker — server must still scope.
    beautician_a.user_permissions.add(Permission.objects.get(codename="confirm_staff_attendance"))

    client_b = Client()
    beautician_b = staff_login(
        client_b,
        permissions=["view_staff_portal", "view_staff_booking", "view_staff_payment_summary"],
    )
    apply_role_permissions(beautician_b, StaffProfile.Role.BEAUTICIAN)
    booking_b.assigned_staff = beautician_b
    booking_b.save(update_fields=["assigned_staff", "updated_at"])

    detail = client_a.get(f"/api/staff/bookings/{booking_b.public_id}/", secure=True)
    assert detail.status_code in {403, 404}

    fulfill = client_a.post(
        f"/api/staff/bookings/{booking_b.public_id}/fulfillment/",
        data={"fulfillment_status": "completed"},
        content_type="application/json",
        secure=True,
    )
    assert fulfill.status_code in {403, 404}
    booking_b.refresh_from_db()
    assert booking_b.fulfillment_status == Booking.FulfillmentStatus.NOT_STARTED


@pytest.mark.django_db(transaction=True)
def test_a08_fulfillment_mass_assignment_ignores_financial_fields():
    """Extra status/amount_paid in fulfillment body must not alter money state."""
    booking = mark_confirmed(_held_booking(key="rt-mass-assign"))
    financial_status = booking.status
    amount = booking.total_price_snapshot

    client = Client()
    staff_login(client, permissions=["confirm_staff_attendance", "view_staff_booking"])
    response = client.post(
        f"/api/staff/bookings/{booking.public_id}/fulfillment/",
        data={
            "fulfillment_status": "completed",
            "status": "paid",
            "amount_paid": 0,
            "total_price_snapshot": "0.00",
            "payment_status": "paid",
        },
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.fulfillment_status == Booking.FulfillmentStatus.COMPLETED
    assert booking.status == financial_status
    assert booking.total_price_snapshot == amount


@pytest.mark.django_db(transaction=True)
def test_a03_search_rejects_short_query_and_survives_wildcard_fuzz():
    """q < 3 → 400; SQL-ish wildcards must not 500."""
    client = Client()
    staff_login(client, permissions=["view_staff_portal"])

    short = client.get("/api/staff/bookings/search/?q=ab", secure=True)
    assert short.status_code == 400
    assert short.status_code != 500

    for fuzz in ("%%%", "'; DROP TABLE bookings;--", "' OR '1'='1", "%_%", "   "):
        response = client.get(f"/api/staff/bookings/search/?q={fuzz}", secure=True)
        assert response.status_code in {200, 400}
        assert response.status_code != 500
        body = response.content.decode("utf-8", errors="ignore").lower()
        assert "traceback" not in body
        assert "operationalerror" not in body


@pytest.mark.django_db(transaction=True)
def test_a01_receptionist_cannot_download_receipt_pdf(settings, tmp_path):
    """Receptionist payment-summary visibility ≠ receipt download."""
    settings.RECEIPT_PDF_ARTIFACT_DIR = str(tmp_path)
    booking, _session, _ledger = _confirm_paid_booking("rt-recv-receipt")
    ReceiptPDFService.ensure_artifact(booking.receipt)

    client = Client()
    receptionist = staff_login(
        client,
        permissions=[
            "view_staff_portal",
            "view_staff_booking",
            "view_staff_payment_summary",
            "confirm_staff_attendance",
            "assign_staff_booking",
        ],
    )
    apply_role_permissions(receptionist, StaffProfile.Role.RECEPTIONIST)
    response = client.get(f"/api/staff/bookings/{booking.public_id}/receipt.pdf", secure=True)
    assert response.status_code == 403
