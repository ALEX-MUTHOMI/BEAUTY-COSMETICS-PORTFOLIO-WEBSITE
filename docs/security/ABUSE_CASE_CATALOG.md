# Abuse Case Catalog

| Domain | Controlled scenario | Protection |
| --- | --- | --- |
| Auth | invalid login and OTP spam | cooldown or composite Redis throttle; generic denial |
| Booking | hold spam, replay, capacity exhaustion | IP throttle, idempotency, transaction/capacity locks |
| Checkout | repeated create, STK retry, detail polling | user/IP scopes plus idempotency |
| Billing | fake webhook replay and malformed callbacks | allowlisted source, generic validation, inbox idempotency |
| Status | opaque-token enumeration and polling | hashed handle/IP scope and generic `404` |
| Gallery/media | scraping, UUID enumeration, malformed/raw path probes | IP scope and generic `404` policy |
| Staff | contact reveal repetition and unauthorized polling | user scope, permission, recent auth, audit, generic denial |
| Errors | malformed JSON, method, UUID, header/query tampering | bounded route admission and generic errors |

Tests use 3–10 local requests with fake providers, clear throttle state, and no
sleeps, external network, active scanning, or uncontrolled concurrency.
