import logging
import math
import time
from functools import wraps

from django.http import JsonResponse
from rest_framework.exceptions import APIException
from rest_framework.throttling import BaseThrottle

from core.abuse import AbuseDecision, abuse_keys, action_event_type, actor_for_request, emit_abuse_event, policy_values
from core.diagnostics import throttle_event
from users import services

logger = logging.getLogger(__name__)

TOKEN_BUCKET_LUA = """
local bucket_key = KEYS[1]
local score_key = KEYS[2]
local action_key = KEYS[3]
local now = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local refill_rate = tonumber(ARGV[3])
local ttl = tonumber(ARGV[4])
local score_window = tonumber(ARGV[5])
local cooldown_score = tonumber(ARGV[6])
local temporary_ban_score = tonumber(ARGV[7])
local waf_candidate_score = tonumber(ARGV[8])
local cooldown_seconds = tonumber(ARGV[9])
local temporary_ban_seconds = tonumber(ARGV[10])
local waf_candidate_seconds = tonumber(ARGV[11])
local early_retry_points = tonumber(ARGV[12])

local function rank(action)
  if action == "waf_candidate" then return 3 end
  if action == "temporary_ban" then return 2 end
  if action == "cooldown" then return 1 end
  return 0
end

local function action_for_score(score)
  if score >= waf_candidate_score then return "waf_candidate", waf_candidate_seconds end
  if score >= temporary_ban_score then return "temporary_ban", temporary_ban_seconds end
  if score >= cooldown_score then return "cooldown", cooldown_seconds end
  return "normal", 0
end

local function add_score(points)
  local score = redis.call("INCRBY", score_key, points)
  redis.call("EXPIRE", score_key, score_window)
  return score
end

-- An existing action means this actor did not honor a previous Retry-After.
-- This branch returns before any application or database work and needs no
-- additional Redis round trip.
local existing_action = redis.call("GET", action_key)
if existing_action then
  local score = add_score(early_retry_points)
  local next_action, next_duration = action_for_score(score)
  local changed = 0
  if rank(next_action) > rank(existing_action) then
    redis.call("SET", action_key, next_action, "EX", next_duration)
    existing_action = next_action
    changed = 1
  end
  local retry_after = math.max(redis.call("TTL", action_key), 1)
  return {0, 0, retry_after, score, existing_action, 1, changed}
end

local bucket = redis.call('HMGET', bucket_key, 'tokens', 'updated_at')
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

redis.call('HSET', bucket_key, 'tokens', tokens, 'updated_at', now)
redis.call('EXPIRE', bucket_key, ttl)

if allowed == 1 then
  return {1, tokens, 0, 0, "normal", 0, 0}
end

-- A regular rate limit event is a small signal. Only repeated events become a
-- route-scoped cooldown, keeping compliant SPA polling on the cheap path.
local score = add_score(1)
local action, action_duration = action_for_score(score)
local changed = 0
if action ~= "normal" then
  redis.call("SET", action_key, action, "EX", action_duration)
  wait_seconds = math.max(wait_seconds, action_duration)
  changed = 1
end
return {0, tokens, wait_seconds, score, action, 0, changed}
"""  # nosec B105 - Redis Lua program text, not a credential.


class RedisTokenBucketThrottle(BaseThrottle):
    """
    Redis-backed token bucket throttle. This avoids per-process memory drift and
    keeps abuse controls consistent across horizontally scaled containers.
    """

    scope = None

    def __init__(self):
        self.wait_seconds = None
        self.abuse_decision = None

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
            # Unknown / missing scope must fail closed (never admit unlimited traffic).
            return False

        capacity, period = self.parse_rate(rate)
        # Redis keys are operational data too: never place raw IP addresses,
        # emails, opaque handles, or user identifiers in the key suffix.
        from hashlib import sha256

        ident = sha256(str(self.get_cache_ident(request, view)).encode("utf-8")).hexdigest()
        key = f"throttle:{self.scope}:{ident}"
        score_key, action_key = abuse_keys(self.scope, actor_for_request(request))
        now = time.time()
        refill_rate = capacity / period
        ttl = math.ceil(period * 2)
        (
            score_window,
            cooldown_score,
            temporary_ban_score,
            waf_candidate_score,
            cooldown_seconds,
            temporary_ban_seconds,
            waf_candidate_seconds,
            early_retry_points,
        ) = policy_values()

        try:
            result = services.get_redis_client().eval(
                TOKEN_BUCKET_LUA,
                3,
                key,
                score_key,
                action_key,
                now,
                capacity,
                refill_rate,
                ttl,
                score_window,
                cooldown_score,
                temporary_ban_score,
                waf_candidate_score,
                cooldown_seconds,
                temporary_ban_seconds,
                waf_candidate_seconds,
                early_retry_points,
            )
        except Exception as exc:
            # Fail closed (no silent admit). Log redis_error_class for stall/NOAUTH diagnosis.
            logger.warning(
                "Redis throttle unavailable for scope=%s; failing closed. redis_error_class=%s",
                self.scope,
                type(exc).__name__,
            )
            throttle_event(
                request,
                scope=self.scope,
                rate=rate,
                allowed=False,
                tokens_remaining="",
                retry_after="5",
                redis_status="unavailable",
                failure_behavior="fail_closed_503",
                redis_error_class=type(exc).__name__,
            )
            raise ThrottleInfrastructureUnavailable() from exc
        allowed = int(result[0]) == 1
        self.wait_seconds = int(result[2])
        self.abuse_decision = AbuseDecision(
            score=int(result[3]),
            action=str(result[4]),
            early_retry=bool(int(result[5])),
            action_changed=bool(int(result[6])),
            retry_after=self.wait_seconds,
        )
        if self.abuse_decision.action_changed:
            emit_abuse_event(
                request,
                event_type=action_event_type(self.abuse_decision),
                scope=self.scope,
                decision=self.abuse_decision,
            )
        throttle_event(
            request,
            scope=self.scope,
            rate=rate,
            allowed=allowed,
            tokens_remaining=result[1],
            retry_after=self.wait_seconds,
            redis_status="ok",
            failure_behavior=(
                "abuse_cooldown_429"
                if not allowed and self.abuse_decision.action != "normal"
                else "limited_429" if not allowed else "allowed"
            ),
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
                response["Retry-After"] = "5"
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
