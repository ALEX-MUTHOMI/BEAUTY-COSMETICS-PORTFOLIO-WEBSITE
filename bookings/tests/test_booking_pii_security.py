import hashlib
import logging

import pytest

from bookings.privacy import (
    decrypt_bytes,
    decrypt_value,
    encrypt_bytes,
    encrypt_value,
    hmac_phone_hash,
    redact_email,
    redact_phone,
)
from bookings.tests.factories import create_customer_profile


def test_hmac_hashes_are_deterministic_and_not_plain_sha256(settings):
    settings.PII_HASH_PEPPER = "pepper-one"
    phone = "+254712345678"

    first = hmac_phone_hash(phone)
    second = hmac_phone_hash(phone)

    assert first == second
    assert first != hashlib.sha256(phone.encode()).hexdigest()

    settings.PII_HASH_PEPPER = "pepper-two"
    assert hmac_phone_hash(phone) != first


def test_encryption_round_trips_without_storing_plaintext(settings):
    settings.PII_ENCRYPTION_KEY = "test-encryption-key"
    raw = "+254712345678"

    encrypted = encrypt_value(raw)

    assert raw not in encrypted
    assert decrypt_value(encrypted) == raw


def test_encrypt_bytes_round_trips_binary_without_plaintext_prefix(settings):
    settings.PII_ENCRYPTION_KEY = "test-encryption-key"
    raw = b"%PDF-1.4\nsecret-bytes"

    sealed = encrypt_bytes(raw)

    assert not sealed.startswith(b"%PDF-")
    assert raw not in sealed
    assert decrypt_bytes(sealed) == raw


@pytest.mark.django_db
def test_customer_profile_stores_redacted_display_and_supports_erasure():
    customer = create_customer_profile(
        full_name="Grace Wanjiku",
        email="grace@example.com",
        phone="+254712345678",
    )

    assert customer.full_name_display == "Grace W."
    assert customer.email_redacted == "g***@example.com"
    assert customer.phone_redacted == "+2547***678"
    assert "grace@example.com" not in str(customer.__dict__)

    customer.erase()
    customer.refresh_from_db()

    assert customer.email_encrypted == ""
    assert customer.phone_encrypted == ""
    assert customer.email_hash_hmac
    assert customer.phone_hash_hmac


def test_raw_pii_is_not_logged(caplog):
    raw_phone = "+254712345678"
    raw_email = "grace@example.com"

    with caplog.at_level(logging.INFO):
        logging.getLogger("bookings").info(
            "customer contact %s %s",
            redact_phone(raw_phone),
            redact_email(raw_email),
        )

    assert raw_phone not in caplog.text
    assert raw_email not in caplog.text
