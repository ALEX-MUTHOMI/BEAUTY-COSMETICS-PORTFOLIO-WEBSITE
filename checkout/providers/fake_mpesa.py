import time

from checkout.providers.base import (
    BaseMpesaProvider,
    MpesaProviderResponse,
    ProviderTimeout,
    ProviderUnavailable,
)


class FakeMpesaProvider(BaseMpesaProvider):
    """
    Deterministic provider for default tests and load simulations.
    It never performs network IO.
    """

    def __init__(self, mode="success", delay_seconds=0):
        self.mode = mode
        self.delay_seconds = delay_seconds
        self._responses = {}

    def initiate_stk_push(
        self,
        phone_number,
        amount,
        account_reference,
        description,
        callback_url,
        idempotency_key,
    ):
        if self.delay_seconds:
            time.sleep(self.delay_seconds)
        if self.mode == "timeout":
            raise ProviderTimeout("Fake M-Pesa timeout")
        if self.mode == "outage":
            raise ProviderUnavailable("Fake M-Pesa outage")
        response = MpesaProviderResponse(
            checkout_request_id=f"fake_ws_CO_{idempotency_key}",
            merchant_request_id=f"fake_merchant_{idempotency_key}",
        )
        self._responses[response.checkout_request_id] = {
            "amount": str(amount),
            "account_reference": account_reference,
        }
        return response

    def simulate_callback(
        self,
        checkout_request_id,
        success=True,
        amount="500.00",
        receipt="QFAKE000001",
    ):
        return {
            "CheckoutRequestID": checkout_request_id,
            "MerchantRequestID": checkout_request_id.replace("fake_ws_CO_", "fake_merchant_"),
            "ResultCode": 0 if success else 1032,
            "Amount": str(amount),
            "MpesaReceiptNumber": receipt if success else "",
        }

    def simulate_malformed_callback(self):
        return {"unexpected": "payload"}

    def simulate_unknown_callback(self):
        return {
            "CheckoutRequestID": "fake_ws_CO_unknown",
            "MerchantRequestID": "fake_merchant_unknown",
            "ResultCode": 0,
            "Amount": "100.00",
            "MpesaReceiptNumber": "QUNKNOWN",
        }
