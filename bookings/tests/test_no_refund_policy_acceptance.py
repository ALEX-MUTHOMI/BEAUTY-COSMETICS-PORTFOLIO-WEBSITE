import pytest

from bookings.services.legal import NO_REFUND_NOTICE, POLICY_ACCEPTANCE_TEXT


def test_checkout_acceptance_text_contains_no_refund_acknowledgement():
    assert "non-refundable" in POLICY_ACCEPTANCE_TEXT.lower()
    assert "rescheduled according to the booking policy" in POLICY_ACCEPTANCE_TEXT.lower()


def test_no_refund_notice_contains_legal_rights_carveout():
    assert "paid bookings are non-refundable" in NO_REFUND_NOTICE.lower()
    assert "nothing in this policy limits rights" in NO_REFUND_NOTICE.lower()


@pytest.mark.django_db
def test_no_billing_refund_or_reversal_endpoint_exposed(client):
    response = client.post("/api/bookings/refund/", secure=True)

    assert response.status_code in {404, 405}
