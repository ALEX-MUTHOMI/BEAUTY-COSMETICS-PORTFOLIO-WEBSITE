from types import SimpleNamespace

from billing.throttles import STKPushRateThrottle
from users.throttles import OTPAnonRateThrottle


def _request(data, ip="203.0.113.10"):
    return SimpleNamespace(data=data, META={"REMOTE_ADDR": ip})


def _cache_ident(throttle, request):
    return throttle.get_cache_ident(request, view=None)


def test_otp_throttle_key_derivation_handles_malformed_body_classes_without_global_key():
    throttle = OTPAnonRateThrottle()
    malformed_bodies = [
        "scanner-string",
        ["array"],
        None,
        123,
        True,
    ]

    for body in malformed_bodies:
        assert _cache_ident(throttle, _request(body)) == "203.0.113.10"


def test_otp_throttle_valid_email_keeps_ip_and_email_scoping():
    throttle = OTPAnonRateThrottle()

    assert (
        _cache_ident(throttle, _request({"email": " Victim@Example.COM "}, ip="203.0.113.20"))
        == "203.0.113.20:victim@example.com"
    )
    assert (
        _cache_ident(throttle, _request({"email": "other@example.com"}, ip="203.0.113.20"))
        == "203.0.113.20:other@example.com"
    )
    assert (
        _cache_ident(throttle, _request({"email": "victim@example.com"}, ip="203.0.113.21"))
        == "203.0.113.21:victim@example.com"
    )


def test_stk_throttle_key_derivation_handles_malformed_body_classes_without_global_key():
    throttle = STKPushRateThrottle()
    malformed_bodies = [
        "scanner-string",
        ["array"],
        None,
        123,
        False,
    ]

    for body in malformed_bodies:
        assert _cache_ident(throttle, _request(body, ip="198.51.100.7")) == "198.51.100.7"


def test_stk_throttle_valid_email_keeps_ip_and_email_scoping():
    throttle = STKPushRateThrottle()

    assert (
        _cache_ident(throttle, _request({"email": " Buyer@Example.COM "}, ip="198.51.100.8"))
        == "198.51.100.8:buyer@example.com"
    )
    assert (
        _cache_ident(throttle, _request({"email": "other@example.com"}, ip="198.51.100.8"))
        == "198.51.100.8:other@example.com"
    )
