# Booking PII data map — GDPR + Kenya DPA 2019

## Scope
Customer fields collected on the public hold → checkout money path.

| Field | Purpose | Lawful basis | Retention |
|-------|---------|--------------|-----------|
| `full_name` | Identify customer for appointment | Contract | 24 months after last completed booking, then soft-delete |
| `email` | Transactional confirmation, receipt, OTP | Contract | 24 months; marketing requires separate consent |
| `phone` | M-Pesa STK / appointment contact | Contract | 24 months; never logged in cleartext |

## Subject rights
- Intake: `POST /api/bookings/privacy/rights-request/` (CSRF + `privacy_rights` throttle)
- Published map: `GET /api/bookings/privacy/data-map/`
- Fulfilment is staff-operated; API returns a ticket id only (no PII echo)

## Observability
- Sentry scrubbers (frontend + backend) redact email, MSISDN, tokens
- Application logs hash contact identifiers on privacy intake
