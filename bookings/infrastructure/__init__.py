"""Infrastructure adapters for external providers and storage in the bookings context.

Infrastructure modules wrap external I/O: email providers, object storage,
PDF generators, payment gateways.  They MUST NOT embed business rules.

For business rules, use bookings.domain.
For mutation workflows, use bookings.services.
For read/presentation logic, use bookings.selectors.
"""
