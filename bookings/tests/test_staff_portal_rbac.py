"""Staff portal RBAC: fulfillment vs payment, receipt lock, search, beautician scope."""

import pytest
from django.test import Client

from bookings.models import Booking, StaffActionAuditEvent, StaffProfile
from bookings.services.staff_roles import apply_role_permissions
from bookings.tests.test_booking_checkout_contract import _held_booking
from bookings.tests.test_staff_portal_helpers import mark_confirmed, staff_login


@pytest.mark.django_db(transaction=True)
def test_fulfillment_does_not_mutate_booking_status():
    booking = mark_confirmed(_held_booking(key="fulfill-indep"))
    financial_status = booking.status
    client = Client()
    staff_login(client, permissions=["confirm_staff_attendance", "view_staff_booking"])
    response = client.post(
        f"/api/staff/bookings/{booking.public_id}/fulfillment/",
        data={"fulfillment_status": "completed"},
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.status == financial_status
    assert booking.fulfillment_status == Booking.FulfillmentStatus.COMPLETED
    assert StaffActionAuditEvent.objects.filter(
        booking=booking,
        action=StaffActionAuditEvent.Action.ATTENDANCE_CONFIRM,
    ).exists()


@pytest.mark.django_db(transaction=True)
def test_receipt_pdf_requires_download_permission_not_summary_alone():
    from bookings.infrastructure.receipt_pdf import ReceiptPDFService
    from bookings.tests.test_booking_receipt_foundation import _confirm_paid_booking

    booking, _session, _ledger = _confirm_paid_booking("rbac-receipt-lock")
    ReceiptPDFService.ensure_artifact(booking.receipt)

    receptionist = Client()
    staff_login(
        receptionist,
        permissions=["view_staff_payment_summary", "view_staff_booking"],
    )
    assert receptionist.get(f"/api/staff/bookings/{booking.public_id}/receipt.pdf", secure=True).status_code == 403

    owner = Client()
    staff_login(owner, permissions=["download_staff_receipt"])
    assert owner.get(f"/api/staff/bookings/{booking.public_id}/receipt.pdf", secure=True).status_code == 200


@pytest.mark.django_db(transaction=True)
def test_search_requires_three_characters():
    client = Client()
    staff_login(client, permissions=["view_staff_portal"])
    short = client.get("/api/staff/bookings/search/?q=ab", secure=True)
    assert short.status_code == 400


@pytest.mark.django_db(transaction=True)
def test_beautician_only_sees_assigned_bookings():
    booking_a = mark_confirmed(_held_booking(key="beaut-a"))
    booking_b = mark_confirmed(_held_booking(key="beaut-b"))

    beautician_client = Client()
    beautician = staff_login(
        beautician_client,
        permissions=["view_staff_portal", "view_staff_booking", "view_staff_payment_summary"],
    )
    apply_role_permissions(beautician, StaffProfile.Role.BEAUTICIAN)
    booking_a.assigned_staff = beautician
    booking_a.save(update_fields=["assigned_staff", "updated_at"])

    day = booking_a.local_booking_date.isoformat()
    schedule = beautician_client.get(f"/api/staff/bookings/schedule/?date={day}", secure=True)
    assert schedule.status_code == 200
    ids = {row["public_booking_id"] for row in schedule.json()["appointments"]}
    assert str(booking_a.public_id) in ids
    assert str(booking_b.public_id) not in ids

    detail_b = beautician_client.get(f"/api/staff/bookings/{booking_b.public_id}/", secure=True)
    assert detail_b.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_assign_and_role_permissions_matrix():
    booking = mark_confirmed(_held_booking(key="assign-1"))
    owner_client = Client()
    owner = staff_login(
        owner_client,
        permissions=[
            "assign_staff_booking",
            "view_staff_booking",
            "view_staff_portal",
        ],
    )
    apply_role_permissions(owner, StaffProfile.Role.OWNER)

    beautician_client = Client()
    beautician = staff_login(
        beautician_client,
        permissions=["view_staff_portal", "view_staff_booking"],
    )
    apply_role_permissions(beautician, StaffProfile.Role.BEAUTICIAN)

    response = owner_client.post(
        f"/api/staff/bookings/{booking.public_id}/assign/",
        data={"assigned_staff_id": beautician.pk},
        content_type="application/json",
        secure=True,
    )
    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.assigned_staff_id == beautician.pk
