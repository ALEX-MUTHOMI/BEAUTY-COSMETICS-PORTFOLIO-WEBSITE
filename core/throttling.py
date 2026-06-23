import hashlib
import logging
import math
import time
from functools import wraps

from django.http import JsonResponse
from rest_framework.exceptions import APIException
from rest_framework.throttling import BaseThrottle

from core.diagnostics import throttle_event
from users import services

logger = logging.getLogger(__name__)

TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local refill_rate = tonumber(ARGV[3])
local ttl = tonumber(ARGV[4])

local bucket = redis.call('HMGET', key, 'tokens', 'updated_at')
local tokens = tonumber(bucket[1])
local updated_at = tonumber(bucket[2])

if tokens == nil then
  tokens = capacity
  updated_at = now
end

local elapsed = math.max(0, now - updated_at)
tokens = math.min(capacity, tokens + (elapsed * refill_rate))

local allowed = 0
local wait_seconds = 0
if tokens >= 1 then
  allowed = 1
  tokens = tokens - 1
else
  wait_seconds = math.ceil((1 - tokens) / refill_rate)
end

redis.call('HSET', key, 'tokens', tokens, 'updated_at', now)
redis.call('EXPIRE', key, ttl)
return {allowed, tokens, wait_seconds}
"""


class RedisTokenBucketThrottle(BaseThrottle):
    """
    Redis-backed token bucket throttle. This avoids per-process memory drift and
    keeps abuse controls consistent across horizontally scaled containers.
    """

    scope = None

    def __init__(self):
        self.wait_seconds = None

    def get_ident(self, request):
        return request.META.get("REMOTE_ADDR", "")

    def get_cache_ident(self, request, view):
        return self.get_ident(request)

    def get_rate(self):
        if not self.scope:
            return None
        return self.THROTTLE_RATES.get(self.scope)

    @property
    def THROTTLE_RATES(self):
        from django.conf import settings

        return settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {})

    def parse_rate(self, rate):
        if not rate:
            return None, None

        num, period = rate.split("/")
        duration = {
            "s": 1,
            "sec": 1,
            "second": 1,
            "m": 60,
            "min": 60,
            "minute": 60,
            "h": 3600,
            "hour": 3600,
            "d": 86400,
            "day": 86400,
        }[period]
        return int(num), duration

    def allow_request(self, request, view):
        rate = self.get_rate()
        if rate is None:
            return True

        capacity, period = self.parse_rate(rate)
        # Redis keys are operational data too: never place raw IP addresses,
        # emails, opaque handles, or user identifiers in the key suffix.
        ident = hashlib.sha256(str(self.get_cache_ident(request, view)).encode("utf-8")).hexdigest()
        key = f"throttle:{self.scope}:{ident}"
        now = time.time()
        refill_rate = capacity / period
        ttl = math.ceil(period * 2)

        try:
            result = services.get_redis_client().eval(
                TOKEN_BUCKET_LUA,
                1,
                key,
                now,
                capacity,
                refill_rate,
                ttl,
            )
        except Exception as exc:
            logger.warning("Redis throttle unavailable for scope=%s; failing closed.", self.scope)
            throttle_event(
                request,
                scope=self.scope,
                rate=rate,
                allowed=False,
                tokens_remaining="",
                retry_after="",
                redis_status="unavailable",
                failure_behavior="fail_closed_503",
            )
            raise ThrottleInfrastructureUnavailable() from exc
        allowed = int(result[0]) == 1
        self.wait_seconds = int(result[2])
        throttle_event(
            request,
            scope=self.scope,
            rate=rate,
            allowed=allowed,
            tokens_remaining=result[1],
            retry_after=self.wait_seconds,
            redis_status="ok",
            failure_behavior="limited_429" if not allowed else "allowed",
        )
        return allowed

    def wait(self):
        return self.wait_seconds


class ThrottleInfrastructureUnavailable(APIException):
    status_code = 503
    default_detail = "Admission control unavailable. Retry later."
    default_code = "admission_control_unavailable"


class RouteRateThrottle(RedisTokenBucketThrottle):
    """A scoped throttle for Django function views that DRF cannot wrap."""

    def __init__(self, scope, key_builder=None):
        super().__init__()
        self.scope = scope
        self.key_builder = key_builder

    def get_cache_ident(self, request, view):
        if self.key_builder:
            return self.key_builder(request)
        return self.get_ident(request)


def staff_or_ip_identity(request):
    user = getattr(request, "user", None)
    if getattr(user, "is_authenticated", False):
        return f"staff:{user.pk}"
    return f"ip:{request.META.get('REMOTE_ADDR', '')}"


def route_throttle(scope, key_builder=None):
    """Return a safe generic admission-control wrapper for function views."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            throttle = RouteRateThrottle(scope, key_builder=key_builder)
            try:
                allowed = throttle.allow_request(request, view_func)
            except ThrottleInfrastructureUnavailable:
                response = JsonResponse({"detail": "Service temporarily unavailable."}, status=503)
                response["Cache-Control"] = "no-store"
                response["X-Content-Type-Options"] = "nosniff"
                return response
            if not allowed:
                response = JsonResponse({"detail": "Too many requests. Please try again later."}, status=429)
                if throttle.wait_seconds:
                    response["Retry-After"] = str(throttle.wait_seconds)
                response["Cache-Control"] = "no-store"
                response["X-Content-Type-Options"] = "nosniff"
                return response
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
