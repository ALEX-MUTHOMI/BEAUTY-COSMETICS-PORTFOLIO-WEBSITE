"""Pure business rules for the bookings bounded context.

Domain modules MUST NOT access the Django ORM (no .objects, no QuerySet,
no transaction.atomic, no select_for_update).  They MAY accept injected
collaborators (e.g. a Redis client) but must not import infrastructure
directly.

For ORM-backed rule enforcement, use bookings.services.
For read/presentation logic, use bookings.selectors.
"""
