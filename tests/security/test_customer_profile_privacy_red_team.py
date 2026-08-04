import pytest

from bookings.models import CustomerProfile


@pytest.mark.django_db
def test_customer_profile_red_team_does_not_store_plaintext_or_marketing_consent():
    profile = CustomerProfile.create_from_plaintext(
        full_name="<img src=x onerror=alert(1)>",
        email="attacker@example.com",
        phone="+254712345678",
    )
    dump = str(profile.__dict__)
    assert "attacker@example.com" not in dump
    assert "+254712345678" not in dump
    assert "onerror" not in profile.full_name_display.lower()
    assert profile.marketing_consent is False
