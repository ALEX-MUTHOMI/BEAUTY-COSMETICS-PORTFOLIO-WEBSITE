import pytest
from django.contrib.auth import get_user_model

from bookings.models import StaffActionAuditEvent
from bookings.services.staff_security import PermissionDenied, reveal_customer_contact, staff_booking_summary
from bookings.tests.factories import create_booking

User = get_user_model()


@pytest.mark.django_db
def test_staff_summary_is_staff_only_and_redacted_by_default():
    booking = create_booking()
    non_staff = User.objects.create_user(email="client@example.com", phone_number="+254700000001")
    staff = User.objects.create_user(email="staff@example.com", phone_number="+254700000002", is_staff=True)

    with pytest.raises(PermissionDenied):
        staff_booking_summary(non_staff, booking)

    summary = staff_booking_summary(staff, booking)

    assert summary["public_id"] == str(booking.public_id)
    assert summary["phone"] == booking.customer_profile.phone_redacted
    assert "phone_encrypted" not in summary
    assert str(booking.id) not in summary.values()


@pytest.mark.django_db
def test_contact_reveal_creates_staff_audit_event():
    booking = create_booking()
    staff = User.objects.create_user(email="staff-reveal@example.com", phone_number="+254700000003", is_staff=True)

    contact = reveal_customer_contact(staff, booking, reason="customer called shop")

    assert contact["phone"]
    assert StaffActionAuditEvent.objects.filter(
        staff=staff,
        booking=booking,
        action=StaffActionAuditEvent.Action.CONTACT_REVEAL,
    ).exists()
