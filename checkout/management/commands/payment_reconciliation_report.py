import json

from django.core.management.base import BaseCommand

from billing.models import FinancialAuditEvent, LedgerTransaction, SettlementRecord
from checkout.models import CheckoutSession, MpesaWebhookInbox


class Command(BaseCommand):
    help = "Print a redacted payment reconciliation summary."

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            choices=[choice.value for choice in MpesaWebhookInbox.Status],
            help="Limit webhook inbox event listing to one processing status.",
        )
        parser.add_argument(
            "--include-events",
            action="store_true",
            help="Include redacted webhook event summaries.",
        )

    def handle(self, *args, **options):
        events = MpesaWebhookInbox.objects.all().order_by("received_at")
        if options.get("status"):
            events = events.filter(processing_status=options["status"])

        counts = {
            status.value: MpesaWebhookInbox.objects.filter(
                processing_status=status.value
            ).count()
            for status in MpesaWebhookInbox.Status
        }
        report = {
            "counts": counts,
            "checkout_statuses": {
                status.value: CheckoutSession.objects.filter(
                    status=status.value
                ).count()
                for status in CheckoutSession.Status
            },
            "ledger": {
                "successful_ledgers": LedgerTransaction.objects.filter(
                    status=LedgerTransaction.Status.SUCCESS
                ).count(),
                "failed_ledgers": LedgerTransaction.objects.filter(
                    status=LedgerTransaction.Status.FAILED
                ).count(),
                "audit_events": FinancialAuditEvent.objects.count(),
                "settlements": SettlementRecord.objects.count(),
            },
            "retry_policy": {
                "failed_events_visible": counts.get(MpesaWebhookInbox.Status.FAILED, 0),
                "automatic_retry_supported": False,
                "reason": (
                    "raw provider payloads are not stored; request provider replay "
                    "or re-ingest a verified callback."
                ),
            },
        }

        if options.get("include_events"):
            report["events"] = [
                {
                    "id": str(event.id),
                    "status": event.processing_status,
                    "correlation_id": event.correlation_id,
                    "redacted_payload": event.redacted_payload,
                }
                for event in events
            ]

        self.stdout.write(json.dumps(report, sort_keys=True))
