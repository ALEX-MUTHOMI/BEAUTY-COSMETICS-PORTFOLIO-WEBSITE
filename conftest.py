import os

import pytest


@pytest.fixture(autouse=True)
def _gallery_test_storage(settings, tmp_path):
    settings.GALLERY_STORAGE_ROOT = tmp_path / "gallery-storage"
    yield


@pytest.fixture(autouse=True)
def _clear_test_cache():
    from django.core.cache import cache

    cache.clear()
    yield


@pytest.fixture(autouse=True)
def _flush_redis_throttle_keys():
    """
    ROOT-CAUSE FIX for Phase 3X matrix instability.

    The throttle system uses direct Redis (via users.services.get_redis_client),
    which bypasses Django's cache framework entirely. cache.clear() above does NOT
    flush throttle:* keys. This caused cross-test pollution where rate-limit tests
    consumed token buckets that persisted into subsequent tests, generating 429s
    and cascading timeouts in the broad security suite.

    This fixture deterministically flushes throttle, abuse, and OTP keys before and
    after each test. SCAN is used instead of KEYS to avoid blocking Redis.
    """
    _flush_operational_redis_keys()
    yield
    _flush_operational_redis_keys()


def _redis_cleanup_is_required():
    from django.conf import settings

    redis_url = str(getattr(settings, "REDIS_URL", ""))
    ci_enabled = os.environ.get("CI", "").lower() in {"1", "true", "yes"}
    return ci_enabled or "@redis:" in redis_url or "//redis:" in redis_url


def _flush_operational_redis_keys():
    """Flush throttle:*, abuse:*, and otp:* keys from direct Redis. Test-only."""
    try:
        from users.services import get_redis_client

        client = get_redis_client()
        for pattern in ("throttle:*", "abuse:*", "otp:*"):
            cursor = 0
            while True:
                cursor, keys = client.scan(cursor, match=pattern, count=200)
                if keys:
                    client.delete(*keys)
                if int(cursor) == 0:
                    break
    except Exception as exc:
        if _redis_cleanup_is_required():
            pytest.fail(f"Required Redis test cleanup failed: {type(exc).__name__}")


def pytest_addoption(parser):
    parser.addoption(
        "--run-external",
        action="store_true",
        default=False,
        help="Run opt-in external provider contract tests.",
    )


def pytest_collection_modifyitems(config, items):
    for item in items:
        path = str(item.path).replace("\\", "/")
        if "/tests/load/" in path:
            item.add_marker(pytest.mark.payment_load)
        if "/tests/security/" in path:
            item.add_marker(pytest.mark.payment_security)
        if "/tests/latency/" in path:
            item.add_marker(pytest.mark.latency)
            item.add_marker(pytest.mark.network_resilience)
        if "/tests/integration/" in path or "daraja" in path or "provider_adapter" in path:
            item.add_marker(pytest.mark.payment_contract)

    if config.getoption("--run-external"):
        return
    skip_external = pytest.mark.skip(reason="external provider tests require --run-external")
    for item in items:
        if "external" in item.keywords:
            item.add_marker(skip_external)
