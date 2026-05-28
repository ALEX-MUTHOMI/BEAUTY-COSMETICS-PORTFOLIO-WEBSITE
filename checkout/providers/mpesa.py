import os
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

from checkout.mpesa import build_stk_push_payload
from checkout.providers.base import (
    BaseMpesaProvider,
    MpesaProviderResponse,
    ProviderTimeout,
    ProviderUnavailable,
)


class MpesaProvider(BaseMpesaProvider):
    """
    Minimal bounded real-provider adapter.
    Default tests use FakeMpesaProvider; this adapter is only for opt-in paths.
    """

    def __init__(self, connect_timeout=None, read_timeout=None):
        self.connect_timeout = connect_timeout or getattr(
            settings, "MPESA_CONNECT_TIMEOUT", 2
        )
        self.read_timeout = read_timeout or getattr(settings, "MPESA_READ_TIMEOUT", 5)
        self.endpoint = os.environ.get("DARAJA_STK_URL", "")

    def initiate_stk_push(
        self,
        phone_number,
        amount,
        account_reference,
        description,
        callback_url,
        idempotency_key,
    ):
        if not self.endpoint:
            raise ProviderUnavailable("M-Pesa STK endpoint is not configured.")
        if urllib.parse.urlparse(self.endpoint).scheme != "https":
            raise ProviderUnavailable("M-Pesa STK endpoint must use HTTPS.")

        payload = build_stk_push_payload(
            phone_number=phone_number,
            amount=amount,
            account_reference=account_reference,
            description=description,
            callback_url=callback_url,
        )
        request = urllib.request.Request(
            self.endpoint, data=str(payload).encode(), method="POST"
        )
        try:
            with urllib.request.urlopen(  # nosec B310
                request, timeout=self.connect_timeout + self.read_timeout
            ):
                pass
        except TimeoutError as exc:
            raise ProviderTimeout("M-Pesa STK request timed out.") from exc
        except urllib.error.URLError as exc:
            raise ProviderUnavailable("M-Pesa STK request failed safely.") from exc

        return MpesaProviderResponse(
            checkout_request_id=f"mpesa_ws_CO_{idempotency_key}",
            merchant_request_id=f"mpesa_merchant_{idempotency_key}",
        )
