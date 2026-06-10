"""Read-only selectors and presentation logic for the bookings bounded context.

Selectors MUST NOT mutate state (no .save(), .create(), .update(), .delete()).
They MAY issue read queries (QuerySet.filter, .first, .get, .aggregate).

For mutation workflows, use bookings.services.
"""
