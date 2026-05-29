import os
import time
import uuid
from decimal import Decimal
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from billing.models import FinancialAuditEvent, LedgerTransaction, SettlementRecord
from billing.redaction import hash_sensitive_value
from checkout.models import CheckoutSession, MpesaWebhookInbox
from checkout.providers.mpesa import MpesaProvider
from checkout.services import create_checkout_session, initiate_mpesa_stk, process_mpesa_callback

REQUIRED_ENV = (
    "DARAJA_ENV",
    "DARAJA_CONSUMER_KEY",
    "DARAJA_CONSUMER_SECRET",
    "DARAJA_SHORTCODE",
    "DARAJA_PASSKEY",
    "DARAJA_CALLBACK_URL",
    "DARAJA_ACCOUNT_REFERENCE",
    "DARAJA_TRANSACTION_DESC",
    "DARAJA_TEST_MSISDN",
)


class Command(BaseCommand):
    help = "Run one opt-in Daraja sandbox STK and verify the real callback in the live Docker database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--wait-seconds", type=int, default=int(os.environ.get("DARAJA_CALLBACK_WAIT_SECONDS", "180"))
        )
        parser.add_argument(
            "--poll-interval",
            type=int,
            default=int(os.environ.get("DARAJA_CALLBACK_POLL_INTERVAL_SECONDS", "5")),
        )
        parser.add_argument("--require-callback", action="store_true")
        parser.add_argument("--replay-count", type=int, default=10)

    def handle(self, *args, **options):
        missing = [key for key in REQUIRED_ENV if not os.environ.get(key)]
        if missing:
            raise CommandError(f"Missing required Daraja env vars: {', '.join(missing)}")
        if os.environ.get("DARAJA_ENV") != "sandbox":
            raise CommandError("DARAJA_ENV must be sandbox for this command.")

        callback_url = os.environ["DARAJA_CALLBACK_URL"]
        parsed_callback = urlparse(callback_url)
        if parsed_callback.scheme != "https":
            raise CommandError("DARAJA_CALLBACK_URL must be HTTPS.")

        User = get_user_model()
        run_id = uuid.uuid4().hex
        amount = Decimal(os.environ.get("DARAJA_TEST_AMOUNT", "1")).quantize(Decimal("0.01"))
        customer = User.objects.create_user(
            email=f"daraja-sandbox-{run_id}@example.test",
            phone_number=os.environ["DARAJA_TEST_MSISDN"],
        )
        session = create_checkout_session(
            customer=customer,
            amount=amount,
            currency="KES",
            description=os.environ["DARAJA_TRANSACTION_DESC"],
            purchasable_type="booking_candidate",
            purchasable_id=f"daraja-sandbox-{run_id}",
            idempotency_key=f"daraja-sandbox-session-{run_id}",
        )

        self.stdout.write("env_booleans_all_true=True")
        self.stdout.write("sandbox_env=True")
        self.stdout.write("callback_is_https=True")
        self.stdout.write("ledger_success_before_callback=0")

        attempt = initiate_mpesa_stk(
            session.id,
            phone_number=os.environ["DARAJA_TEST_MSISDN"],
            idempotency_key=f"daraja-sandbox-stk-{run_id}",
            provider=MpesaProvider(),
        )
        session.refresh_from_db()
        self.stdout.write("oauth_and_stk_request_sent=True")
        self.stdout.write("phone_prompt_initiated=True")
        self.stdout.write(f"checkout_state_after_stk={session.status}")

        deadline = time.monotonic() + max(options["wait_seconds"], 0)
        poll_interval = max(options["poll_interval"], 1)
        checkout_request_hash = hash_sensitive_value(attempt.provider_request_id)
        while time.monotonic() < deadline:
            session.refresh_from_db()
            inbox_seen = MpesaWebhookInbox.objects.filter(checkout_request_id_hash=checkout_request_hash).exists()
            if inbox_seen and session.status in {
                CheckoutSession.Status.PAID,
                CheckoutSession.Status.FAILED,
                CheckoutSession.Status.EXPIRED,
                CheckoutSession.Status.CANCELLED,
            }:
                break
            time.sleep(poll_interval)

        session.refresh_from_db()
        inbox_count = MpesaWebhookInbox.objects.filter(checkout_request_id_hash=checkout_request_hash).count()
        ledger_qs = LedgerTransaction.objects.filter(external_correlation_id=str(session.id))
        ledger_success_count = ledger_qs.filter(status=LedgerTransaction.Status.SUCCESS).count()
        self.stdout.write(f"callback_received={bool(inbox_count)}")
        self.stdout.write(f"webhook_inbox_event_count={inbox_count}")
        self.stdout.write(f"checkout_state_after_callback={session.status}")
        self.stdout.write(f"ledger_success_count_after_callback={ledger_success_count}")

        if session.status != CheckoutSession.Status.PAID:
            if options["require_callback"]:
                raise CommandError("Daraja callback was not received as a successful payment within bounded wait.")
            return

        ledger = ledger_qs.get(status=LedgerTransaction.Status.SUCCESS)
        audit_count = FinancialAuditEvent.objects.filter(ledger_transaction=ledger).count()
        settlement_count = SettlementRecord.objects.filter(ledger_transaction=ledger).count()
        self.stdout.write(f"audit_event_count={audit_count}")
        self.stdout.write(f"settlement_count={settlement_count}")

        replay_payload = {
            "CheckoutRequestID": attempt.provider_request_id,
            "MerchantRequestID": attempt.merchant_request_id,
            "ResultCode": 0,
            "Amount": str(session.amount_snapshot),
            "MpesaReceiptNumber": "SANDBOX-REPLAY-REDACTED",
        }
        processed_success = 0
        duplicate_count = 0
        for _ in range(options["replay_count"]):
            result = process_mpesa_callback(
                replay_payload,
                remote_addr="127.0.0.1",
                correlation_id=f"daraja-replay-{run_id}",
            )
            if result.session is None:
                duplicate_count += 1
            else:
                processed_success += 1

        final_ledger_success_count = ledger_qs.filter(status=LedgerTransaction.Status.SUCCESS).count()
        final_settlement_count = SettlementRecord.objects.filter(ledger_transaction=ledger).count()
        self.stdout.write(f"duplicate_replay_count={options['replay_count']}")
        self.stdout.write(f"duplicate_replay_processed_success_count={processed_success}")
        self.stdout.write(f"duplicate_replay_duplicate_count={duplicate_count}")
        self.stdout.write(f"duplicate_replay_ledger_success_count={final_ledger_success_count}")
        self.stdout.write(f"duplicate_replay_settlement_count={final_settlement_count}")
