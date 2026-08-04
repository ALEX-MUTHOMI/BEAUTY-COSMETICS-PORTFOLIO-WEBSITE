"""Bounded, privacy-safe abuse escalation primitives.

This module never persists raw actor values. It is intentionally Redis-only so
normal request admission remains inexpensive and abuse accounting does not add
database load during an attack.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass

from django.conf import settings

logger = logging.getLogger("core.abuse")

ABUSE_SIGNAL_LUA = """
local score_key = KEYS[1]
local action_key = KEYS[2]
local points = tonumber(ARGV[1])
local score_window = tonumber(ARGV[2])
local cooldown_score = tonumber(ARGV[3])
local temporary_ban_score = tonumber(ARGV[4])
local waf_candidate_score = tonumber(ARGV[5])
local cooldown_seconds = tonumber(ARGV[6])
local temporary_ban_seconds = tonumber(ARGV[7])
local waf_candidate_seconds = tonumber(ARGV[8])

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

local score = redis.call("INCRBY", score_key, points)
redis.call("EXPIRE", score_key, score_window)
local current_action = redis.call("GET", action_key) or "normal"
local next_action, next_duration = action_for_score(score)
local changed = 0

if rank(next_action) > rank(current_action) then
  redis.call("SET", action_key, next_action, "EX", next_duration)
  current_action = next_action
  changed = 1
end

local retry_after = 0
if current_action ~= "normal" then
  retry_after = math.max(redis.call("TTL", action_key), 1)
end
return {score, current_action, retry_after, changed}
"""


@dataclass(frozen=True)
class AbuseActor:
    actor_type: str
    actor_hash: str


@dataclass(frozen=True)
class AbuseDecision:
    score: int
    action: str
    retry_after: int
    action_changed: bool
    early_retry: bool = False


def _hash(value: object) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def actor_for_request(request) -> AbuseActor:
    user = getattr(request, "user", None)
    if getattr(user, "is_authenticated", False):
        actor_type = "staff" if getattr(user, "is_staff", False) else "customer"
        return AbuseActor(actor_type, _hash(f"{actor_type}:{user.pk}"))

    session = getattr(request, "session", None)
    session_key = getattr(session, "session_key", None)
    if session_key:
        return AbuseActor("session", _hash(f"session:{session_key}"))
    return AbuseActor("anonymous_ip", _hash(f"ip:{request.META.get('REMOTE_ADDR', '')}"))


def abuse_keys(scope: str, actor: AbuseActor) -> tuple[str, str]:
    suffix = f"{scope}:{actor.actor_type}:{actor.actor_hash}"
    return f"abuse:score:{suffix}", f"abuse:action:{suffix}"


def policy_values() -> tuple[int, int, int, int, int, int, int, int]:
    return (
        int(getattr(settings, "ABUSE_SCORE_WINDOW_SECONDS", 600)),
        int(getattr(settings, "ABUSE_COOLDOWN_SCORE", 4)),
        int(getattr(settings, "ABUSE_TEMPORARY_BAN_SCORE", 11)),
        int(getattr(settings, "ABUSE_WAF_CANDIDATE_SCORE", 16)),
        int(getattr(settings, "ABUSE_COOLDOWN_SECONDS", 300)),
        int(getattr(settings, "ABUSE_TEMPORARY_BAN_SECONDS", 900)),
        int(getattr(settings, "ABUSE_WAF_CANDIDATE_SECONDS", 3600)),
        int(getattr(settings, "ABUSE_EARLY_RETRY_POINTS", 2)),
    )


def action_event_type(decision: AbuseDecision) -> str:
    if decision.early_retry:
        return "RETRY_AFTER_IGNORED"
    if decision.action == "temporary_ban":
        return "TEMP_BAN_APPLIED"
    if decision.action == "waf_candidate":
        return "WAF_CANDIDATE"
    return "ROUTE_COOLDOWN_APPLIED"


def emit_abuse_event(
    request, *, event_type: str, scope: str, decision: AbuseDecision, redis_status: str = "ok"
) -> None:
    """Emit only redacted, small escalation events; never log request content."""
    actor = actor_for_request(request)
    match = getattr(request, "resolver_match", None)
    route_name = getattr(match, "view_name", None) or "unresolved"
    payload = {
        "event_type": event_type,
        "route_name": route_name,
        "actor_type": actor.actor_type,
        "actor_hash": actor.actor_hash,
        "throttle_scope": scope,
        "action_taken": decision.action,
        "retry_after": decision.retry_after,
        "abuse_score": decision.score,
        "status_family": "4xx",
        "redis_status": redis_status,
        "correlation_id_hash": _hash(getattr(request, "correlation_id", "")),
    }
    logger.warning("abuse_event=%s", json.dumps(payload, sort_keys=True, separators=(",", ":")))


def record_abuse_signal(request, *, scope: str, event_type: str, points: int) -> AbuseDecision | None:
    """Score a suspicious denial without changing its existing HTTP response."""
    from users.services import get_redis_client

    actor = actor_for_request(request)
    score_key, action_key = abuse_keys(scope, actor)
    score_window, cooldown_score, temporary_ban_score, waf_score, cooldown_seconds, ban_seconds, waf_seconds, _ = (
        policy_values()
    )
    try:
        result = get_redis_client().eval(
            ABUSE_SIGNAL_LUA,
            2,
            score_key,
            action_key,
            points,
            score_window,
            cooldown_score,
            temporary_ban_score,
            waf_score,
            cooldown_seconds,
            ban_seconds,
            waf_seconds,
        )
    except Exception:
        return None

    decision = AbuseDecision(
        score=int(result[0]),
        action=str(result[1]),
        retry_after=max(int(result[2]), 0),
        action_changed=bool(int(result[3])),
    )
    if decision.action_changed:
        emit_abuse_event(
            request,
            event_type=event_type if decision.action == "cooldown" else action_event_type(decision),
            scope=scope,
            decision=decision,
        )
    return decision
