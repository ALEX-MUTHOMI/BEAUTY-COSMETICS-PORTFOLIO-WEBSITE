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

Do not expose these through frontend or `NUXT_PUBLIC_*` variables.

## Local Fake Provider

The fake provider normalizes successful sends and returns a deterministic provider message identifier. It does not perform network calls and is the only provider used by default tests.

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
monthly confirmed bookings x 2 emails = minimum monthly transactional emails
```

Provider pricing changes. Verify current Resend/Mailgun pricing before production. Track attachment bandwidth separately if PDFs are attached.

## PDF Attachment Versus Secure Link

Recommended production approach: send a secure receipt download link by default. Attach PDF receipts only if deliverability remains good and provider cost/bandwidth is acceptable. Links reduce email size and improve retry behavior on slow mobile networks.

## Security Policy

These are transactional emails only. Marketing requires separate consent. Emails and PDFs must not contain raw phone numbers, raw email addresses, raw provider callback payloads, M-Pesa receipt numbers, checkout request IDs, merchant request IDs, internal UUID correlations, tokens, API keys, or encrypted field values.
