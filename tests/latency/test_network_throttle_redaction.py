import logging

from checkout.redaction import redact_checkout_payload


def test_slow_network_log_context_redacts_payment_identifiers(caplog):
    with caplog.at_level(logging.INFO):
        logging.getLogger("checkout.latency").info(
            "slow-network=%s",
            redact_checkout_payload(
                {
                    "PhoneNumber": "+254712730006",
                    "CheckoutRequestID": "ws_CO_LATENCY_SECRET",
                    "MerchantRequestID": "merchant_LATENCY_SECRET",
                    "access_token": "token-latency-secret",
                }
            ),
        )

    assert "+254712730006" not in caplog.text
    assert "ws_CO_LATENCY_SECRET" not in caplog.text
    assert "merchant_LATENCY_SECRET" not in caplog.text
    assert "token-latency-secret" not in caplog.text
