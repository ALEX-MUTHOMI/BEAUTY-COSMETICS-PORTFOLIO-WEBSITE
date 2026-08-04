from pathlib import Path


def test_privacy_policy_documents_international_customer_baseline():
    privacy = Path("docs/legal/PRIVACY_POLICY.md").read_text(encoding="utf-8")
    booking = Path("docs/legal/BOOKING_CANCELLATION_RESCHEDULE_POLICY.md").read_text(encoding="utf-8")

    assert "GDPR-grade privacy baseline" in privacy
    assert "Appointment truth remains Africa/Nairobi" in privacy
    assert "Africa/Nairobi" in booking
    assert "Draft for legal review before production." in privacy
