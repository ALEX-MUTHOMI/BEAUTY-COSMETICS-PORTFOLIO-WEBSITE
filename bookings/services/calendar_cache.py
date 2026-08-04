"""Short-lived Redis cache for calendar builds with capacity-aware invalidation."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import date
from typing import Any

from bookings.models import BOOKING_BLOCKING_STATUSES

logger = logging.getLogger("bookings.calendar_cache")

CALENDAR_CACHE_TTL_SECONDS = 45
CAPACITY_GEN_PREFIX = "calendar:capacity_gen:"
CACHE_KEY_PREFIX = "calendar:build:"
BLOCKING_CAPACITY_STATUSES = frozenset(BOOKING_BLOCKING_STATUSES)


def _capacity_gen_key(local_date: date) -> str:
    return f"{CAPACITY_GEN_PREFIX}{local_date.isoformat()}"


def _resolve_redis_client(redis_client=None):
    if redis_client is not None:
        return redis_client
    try:
        from users.services import get_redis_client

        return get_redis_client()
    except Exception:
        return None


def bump_capacity_generation(local_date: date | None, *, redis_client=None) -> None:
    """Bump the capacity generation token for a booking date."""
    if local_date is None:
        return
    client = _resolve_redis_client(redis_client)
    if client is None:
        return
    try:
        client.incr(_capacity_gen_key(local_date))
    except Exception:
        logger.info(
            "calendar.cache.capacity_bump_degraded",
            extra={"local_date": local_date.isoformat()},
        )


def invalidate_calendar_capacity_for_booking(booking, *, redis_client=None) -> None:
    bump_capacity_generation(getattr(booking, "local_booking_date", None), redis_client=redis_client)


def invalidate_calendar_capacity_for_transition(
    *, old_status: str, new_status: str, local_date: date | None, redis_client=None
) -> None:
    if local_date is None or old_status == new_status:
        return
    if old_status in BLOCKING_CAPACITY_STATUSES or new_status in BLOCKING_CAPACITY_STATUSES:
        bump_capacity_generation(local_date, redis_client=redis_client)


def _read_capacity_generation(dates: list[date], redis_client) -> str:
    if not dates:
        return "0"
    try:
        keys = [_capacity_gen_key(current) for current in dates]
        values = redis_client.mget(keys)
        return "|".join(
            f"{current.isoformat()}:{value or '0'}" for current, value in zip(dates, values or [], strict=False)
        )
    except Exception:
        return "0"


class CalendarCache:
    @staticmethod
    def build_key(
        *,
        selection_public_id,
        offered_dates: list[date],
        resource_id=None,
        redis_client=None,
    ) -> str | None:
        client = _resolve_redis_client(redis_client)
        if client is None or not offered_dates:
            return None
        dates_blob = ",".join(current.isoformat() for current in offered_dates)
        capacity_gen = _read_capacity_generation(offered_dates, client)
        resource_part = str(resource_id or "")
        digest = hashlib.sha256(
            f"{selection_public_id}|{dates_blob}|{capacity_gen}|{resource_part}".encode()
        ).hexdigest()
        return f"{CACHE_KEY_PREFIX}{digest}"

    @staticmethod
    def get_payload(cache_key: str | None, redis_client=None) -> dict | None:
        if not cache_key:
            return None
        client = _resolve_redis_client(redis_client)
        if client is None:
            return None
        try:
            raw = client.get(cache_key)
            if not raw:
                return None
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                return None
            return payload
        except Exception:
            logger.info("calendar.cache.read_degraded", extra={"cache_key_prefix": CACHE_KEY_PREFIX})
            return None

    @staticmethod
    def set_payload(cache_key: str | None, payload: dict, redis_client=None) -> None:
        if not cache_key:
            return
        client = _resolve_redis_client(redis_client)
        if client is None:
            return
        try:
            client.setex(
                cache_key, CALENDAR_CACHE_TTL_SECONDS, json.dumps(payload, separators=(",", ":"), sort_keys=True)
            )
        except Exception:
            logger.info("calendar.cache.write_degraded", extra={"cache_key_prefix": CACHE_KEY_PREFIX})

    @staticmethod
    def status_histogram(days: list[dict[str, Any]]) -> dict[str, int]:
        histogram: dict[str, int] = {}
        for day in days:
            status = str(day.get("status") or "unknown")
            histogram[status] = histogram.get(status, 0) + 1
        return histogram
