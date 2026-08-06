"""Throttle fail-closed contracts."""

from unittest.mock import MagicMock

from core.throttling import RedisTokenBucketThrottle


def test_missing_throttle_rate_denies_request():
    throttle = RedisTokenBucketThrottle()
    throttle.scope = "does_not_exist_in_settings"
    assert throttle.get_rate() is None
    assert throttle.allow_request(MagicMock(), MagicMock()) is False
