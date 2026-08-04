# Booking Email And Receipt Delivery

## Provider Decision

Default local and CI behavior uses `EMAIL_PROVIDER=fake`. The production-ready provider interface supports Resend first and keeps Mailgun as a compatible implementation path. External provider tests are opt-in only and must never run in default CI.

## Environment Variables

- `EMAIL_PROVIDER=fake|console|resend|mailgun`
- `EMAIL_FROM_ADDRESS`
- `EMAIL_REPLY_TO_ADDRESS`
- `EMAIL_PROVIDER_API_KEY`
- `EMAIL_PROVIDER_BASE_URL`
- `EMAIL_SEND_TIMEOUT_SECONDS=5`
- `EMAIL_EXTERNAL_TEST_RECIPIENT`
- `RUN_EXTERNAL_EMAIL_TESTS=false`
- `RECEIPT_PDF_TIMEOUT_SECONDS=5`
- `RECEIPT_PDF_MAX_BYTES=250000`
- `RECEIPT_PDF_ARTIFACT_DIR=/app/var/receipt-artifacts`
- `EMAIL_NOTIFICATION_MAX_ATTEMPTS=3`
- `EMAIL_DAILY_SOFT_LIMIT=80`
- `EMAIL_DAILY_HARD_LIMIT=100`
- `EMAIL_MONTHLY_SOFT_LIMIT=2500`
- `EMAIL_MONTHLY_HARD_LIMIT=3000`
- `EMAIL_QUOTA_MODE=queue_only|backup_provider|admin_hold`
- `EMAIL_BACKUP_PROVIDER_ENABLED=false`
- `EMAIL_BACKUP_PROVIDER=mailgun`
- `EMAIL_BACKLOG_HIGH_WATERMARK=100`

Do not expose these through frontend or `NUXT_PUBLIC_*` variables.

## Local Fake Provider

The fake provider normalizes successful sends and returns a deterministic provider message identifier. It does not perform network calls and is the only provider used by default tests. B4D adds a redacted fake outbox contract so CI can prove that exactly one combined confirmation/receipt email was accepted with exactly one PDF attachment, without exposing raw recipient email, phone, provider references, receipt tokens, or API keys.

## External Provider Test

Run only with explicit env and `--run-external`:

```bash
docker compose exec web poetry run pytest tests/external/test_email_provider_sandbox.py -vv --run-external
```

The test must use a designated test recipient only. Do not use production customer data.

## Domain Verification

Before production sending, configure and verify SPF, DKIM, and DMARC for the sending domain. Resend and Mailgun both require provider-side domain verification for reliable deliverability.

## Bounce And Complaint Handling

Production must add webhook handling for bounces, complaints, suppressions, and provider delivery failures before high-volume use. Store only redacted recipient metadata and provider message hashes.

## Volume And Cost Formula

Minimum transactional email volume:

```text
confirmed bookings x 1 combined email = minimum transactional emails
```

Provider pricing changes. Verify current Resend/Mailgun pricing before production. Free-tier daily/monthly limits are acceptable only for early low-volume testing. If daily bookings can exceed the free daily limit, use a paid Resend plan or a verified backup provider before production. A viral 300-booking day must be treated as a paid-plan/backlog scenario, not an application failure.

Do not hardcode provider limits as permanent truth. Verify provider limits before production and before any launch campaign.

## PDF Attachment Versus Secure Link

Default production design: send one combined "Booking confirmed and payment received" email with a low-byte PDF receipt attached. Do not use a public receipt download link as the production default. A future customer portal may support OTP/session-protected re-download.

The receipt PDF target size is 50 KB to 150 KB, with a hard default limit of 250 KB. The PDF is generated once per `BookingReceipt`, stored as a `ReceiptPDFArtifact`, and reused on provider retries. Regeneration is allowed only when the artifact is missing, corrupted, or explicitly marked regeneratable by admin/system policy.

## Queue Isolation And Failure Policy

Receipt PDF generation and email delivery use the `receipts` Celery queue through `bookings.tasks.process_booking_notification` and `bookings.tasks.sweep_booking_notifications`. Payment callbacks remain on the `billing` queue. This prevents receipt rendering/provider latency from starving Daraja/checkout callback processing.

After `EMAIL_NOTIFICATION_MAX_ATTEMPTS`, notifications move to `failed_final` for future admin dashboard review. Provider quota exhaustion moves notifications to `quota_blocked` with a future retry time. Old failed notifications do not block new notifications because the outbox worker processes bounded batches.

B4D CI parity status: local Docker and CI must run fake-provider delivery through the same container path. `ReceiptPDFArtifact` storage must be writable in the container, and fake-provider tests must assert the PDF attachment exists instead of only asserting that an outbox row exists. Safe diagnostics are limited to `failure_code`, `last_error_redacted`, notification status, receipt status, PDF artifact status, provider name, and provider mode.

## Quota And Backlog Runbook

Soft-limit event: `email.quota.soft_limit_reached`. Continue sending while the provider accepts mail and alert operators.

Hard-limit event: `email.quota.hard_limit_reached`. Stop sending through the provider for that window, keep notifications queued/blocked, and retry after reset. If no verified backup provider exists, stay in `queue_only`.

Backlog event: `email.notification.backlog_high`. Operators should review pending, retry-scheduled, quota-blocked, and failed-final counts. Customer-safe wording: "Your booking is confirmed. Receipt email is queued and will be sent shortly."

Provider setup checklist before production: domain verification, SPF, DKIM, DMARC, bounce handling, complaint handling, from-address policy, paid-plan quota, and opt-in external delivery test.

Viral-day policy: 300 confirmed bookings/day requires either a paid provider plan, verified backup provider, or queue-only delay. In queue-only mode, bookings remain confirmed, receipts remain durable, and the customer status endpoint must show delayed/queued receipt email state without exposing provider quota details.

1000-notification backlog policy: process bounded batches, do not tight-loop quota-blocked rows, do not regenerate PDFs on every retry, and do not let notification backlog block booking confirmation or payment callback processing.

## Customer Status Fallback

After checkout/payment, the frontend should redirect to:

```text
/booking/status/<booking_public_id>/
```

The backend status API is:

```text
GET /api/bookings/status/<booking_public_id>/
```

The response is data-minimized and customer-safe. It may show booking, payment, receipt, email, schedule, service, and next-action status. It must not expose raw phone, raw email, customer full name, internal database IDs, checkout IDs, ledger IDs, receipt download tokens, provider references, quota error codes, or stack traces.

Customer-safe fallback messages:

- "Your booking is confirmed."
- "Your receipt email is being prepared."
- "Your receipt email is queued and will be sent shortly."
- "Your payment is being verified. Keep this booking reference."

Do not show provider internals such as "Resend quota exceeded", "provider 429", "ledger mismatch", or "email provider failed".

## B5 Reminder And OTP Notification Policy

Booking reminders and customer OTP messages use outbox/worker semantics. They must not be sent synchronously during booking creation, payment callback processing, receipt generation, or status polling. Default local and CI execution uses the fake provider only.

Reminder rows are created after confirmed bookings and are idempotent per booking, reminder type, and scheduled time. Delivery is bounded by worker `limit`, revalidates booking status, customer erasure, and reminder consent, then sends safe appointment content. Provider errors are redacted and retried with backoff until the configured attempt cap, after which the row moves to admin review. One failed reminder must not block newer reminder or receipt notifications.

Customer OTP messages are for sensitive actions only. OTP is never required for booking creation, payment, or the minimal status page. OTP notifications are queued through the existing notification outbox with recipient HMAC/redacted metadata; raw OTP codes are never stored in the database or logs. OTP request and verify responses remain generic to prevent booking or email enumeration.

No-refund messaging must remain customer-safe and must not expose any refund action or Billing reversal pathway. Customer communications should direct paid customers to policy-controlled rescheduling or support review, not self-service refunds.

## Production Checklist

Before production email sending, verify:

- Sending domain is verified.
- SPF is configured.
- DKIM is configured.
- DMARC is configured.
- Provider API key is stored only in backend secret storage.
- Real opt-in external send test passes.
- Bounce and complaint handling exists.
- Notification worker is deployed.
- `receipts` queue is deployed and monitored.
- Backlog and quota alerts are wired to operators.
- Customer status endpoint is monitored.
- Provider limits are checked before launch.

## Security Policy

These are transactional emails only. Marketing requires separate consent. Emails and PDFs must not contain raw phone numbers, raw email addresses, raw provider callback payloads, M-Pesa receipt numbers, checkout request IDs, merchant request IDs, internal UUID correlations, tokens, API keys, or encrypted field values.
