from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import DataError, IntegrityError

from billing.models import LedgerTransaction

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(email="billing-unit@beauty.com", phone_number="+254712000002")


@pytest.mark.django_db
def test_ledger_transaction_saves_with_expected_defaults(user):
    ledger = LedgerTransaction.objects.create(
        user=user,
        amount=Decimal("999.50"),
        checkout_request_id="billing-unit-save-001",
    )

    assert ledger.id
    assert ledger.status == LedgerTransaction.Status.PENDING
    assert ledger.mpesa_receipt_number is None
    assert ledger.amount == Decimal("999.50")


@pytest.mark.django_db
def test_ledger_transaction_accepts_decimal_field_maximum(user):
    ledger = LedgerTransaction(
        user=user,
        amount=Decimal("9999999999.99"),
        checkout_request_id="billing-unit-max-001",
    )

    ledger.full_clean()
    ledger.save()
    assert ledger.amount == Decimal("9999999999.99")


@pytest.mark.django_db
def test_ledger_transaction_rejects_amount_beyond_decimal_field(user):
    ledger = LedgerTransaction(
        user=user,
        amount=Decimal("10000000000.00"),
        checkout_request_id="billing-unit-overflow-001",
    )

    with pytest.raises((ValidationError, DataError)):
        ledger.full_clean()


@pytest.mark.django_db(transaction=True)
def test_ledger_checkout_request_id_unique_constraint_enforced(user):
    LedgerTransaction.objects.create(
        user=user,
        amount=Decimal("100.00"),
        checkout_request_id="billing-unit-unique-001",
    )

    with pytest.raises((IntegrityError, ValidationError)):
        LedgerTransaction.objects.create(
            user=user,
            amount=Decimal("200.00"),
            checkout_request_id="billing-unit-unique-001",
        )
