# Phase 3D Rate-Limit and Abuse Patch Backlog

Production readiness: **rejected / not claimed**.

| ID | Severity | Route | Actor | Abuse type | Observed behavior | Risk | Recommended action | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3D-HIGH-001 | High | booking hold and checkout bridge | anonymous | spam/replay pressure | idempotency existed but no HTTP admission control | capacity/database pressure | route-specific Redis scopes | Closed |
| 3D-HIGH-002 | High | staff contact reveal | staff | repeated sensitive reveal | audit/reauth existed but no rate limit | excessive PII access | staff-user route scope | Closed |
| 3D-MED-001 | Medium | gallery/media, status, availability, CSRF | anonymous | scrape/enumerate/poll | generic denial/caps without route admission control | resource pressure | IP route scopes | Closed |
| 3D-LOW-001 | Low | staff read-only routes | staff | polling | permissioned/redacted but no dedicated polling scope | operational load | production tuning after telemetry | tracked |
| 3D-MED-002 | Medium | checkout detail | authenticated customer + IP | throttle oracle | DRF default body revealed exact retry window | route policy detail disclosure | generic exception renderer plus `Retry-After` header | Closed |
| 3D-MED-003 | Medium | booking status, checkout detail, public gallery | test actor | synthetic pressure mistaken for normal use | 100/1,000 immediate reads hit production admission policy | misleading 429 test collapse | copied test-only settings plus restoration assertions | Closed |
| 3D-LOW-002 | Low | public booking status SPA | customer | retry UX integration | no public caller consumes the retry helper | a retryable 429 lacks a dedicated customer retry state | wire the existing helper when the public page is introduced | tracked |

Webhook replay remains covered by provider-IP admission and event idempotency.
It is not assigned a narrow request throttle because rejecting valid provider
retries could impair payment reconciliation.

No critical or high finding remains open after the route-scope patch and final
local regression matrix. GitHub CI remains unverified until an approved push.
