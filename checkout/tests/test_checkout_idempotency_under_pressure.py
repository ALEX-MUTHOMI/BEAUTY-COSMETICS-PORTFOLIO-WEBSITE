from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import close_old_connections

from checkout.models import CheckoutSession
from checkout.services import create_checkout_session

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_checkout_session_idempotency_survives_concurrent_reuse():
    customer = User.objects.create_user(email="idem-pressure@aesthetic-os.test", phone_number="+254712600010")

    def create_once():
        close_old_connections()
        try:
            return create_checkout_session(
                customer,
                Decimal("1000.00"),
                "KES",
                "Idempotency",
                "booking_candidate",
                "idem-pressure",
                "idem-pressure-key",
            ).id
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(create_once) for _ in range(100)]
        ids = [future.result(timeout=15) for future in as_completed(futures)]

    assert len(set(ids)) == 1
    assert CheckoutSession.objects.filter(idempotency_key="idem-pressure-key").count() == 1
