# Compatibility wrapper. Canonical implementation lives in bookings.domain.circuit_breaker.
# New code should import from bookings.domain.circuit_breaker.
from bookings.domain.circuit_breaker import *  # noqa: F401,F403
from bookings.domain.circuit_breaker import BookingCircuitBreaker  # noqa: F811

__all__ = ["BookingCircuitBreaker"]
