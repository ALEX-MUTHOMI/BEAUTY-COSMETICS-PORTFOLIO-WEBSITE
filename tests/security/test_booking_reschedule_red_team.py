import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import CustomerOTPChallenge
from bookings.services.customer_otp import CustomerOTPService
from bookings.services.rescheduling import BookingRescheduleService
from bookings.tests.factories import create_booking


@pytest.mark.django_db(transaction=True)
def test_reschedule_red_team_requires_scope_rejects_overlap_xss_and_no_refund():
    victim = create_booking(status="confirmed", starts_at=timezone.now() + timezone.timedelta(days=5))
    other = create_booking(
        status="confirmed",
        resource=victim.resource,
        service=victim.service,
        starts_at=victim.starts_at + timezone.timedelta(days=1),
        ends_at=victim.ends_at + timezone.timedelta(days=1),
        idempotency_key="reschedule-overlap-target",
    )
    challenge = CustomerOTPService.request_challenge(
        booking_public_id=victim.public_id,
        email="grace@example.com",
        purpose=CustomerOTPChallenge.Purpose.RESCHEDULE,
        request_meta={"ip": "203.0.113.51", "user_agent": "<script>"},
    )
    action = CustomerOTPService.verify_challenge(challenge.public_id, CustomerOTPService._last_test_code)

    with pytest.raises(ValidationError):
        BookingRescheduleService.reschedule(
            booking_public_id=other.public_id,
            action_token=action.token,
            requested_starts_at=victim.starts_at + timezone.timedelta(days=2),
        )
    with pytest.raises(ValidationError):
        BookingRescheduleService.reschedule(
            booking_public_id=victim.public_id,
            action_token=action.token,
            requested_starts_at=other.starts_at,
            reason="<script>refund me</script>",
        )
    victim.refresh_from_db()
    assert victim.status == "confirmed"
    assert "refund" not in str(victim.audit_events.values_list("metadata_redacted", flat=True)).lower()
