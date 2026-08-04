import pytest

from bookings.models import CustomerProfile
from bookings.privacy import hmac_email_hash, hmac_phone_hash


@pytest.mark.django_db
def test_customer_profile_pii_is_encrypted_hmaced_redacted_and_indexed():
    profile = CustomerProfile.create_from_plaintext(
        full_name="<script>Grace</script> Wanjiku",
        email="Grace@Example.com",
        phone="+254712345678",
    )

    assert "Grace@Example.com" not in profile.email_encrypted
    assert "+254712345678" not in profile.phone_encrypted
    assert profile.email_hash_hmac == hmac_email_hash("grace@example.com")
    assert profile.phone_hash_hmac == hmac_phone_hash("+254712345678")
    assert profile.email_redacted == "g***@example.com"
    assert profile.phone_redacted == "+2547***678"
    assert profile.marketing_consent is False
    index_names = {index.name for index in CustomerProfile._meta.indexes}
    assert "bk_cust_phone_hash_idx" in index_names
    assert "bk_cust_email_hash_idx" in index_names
