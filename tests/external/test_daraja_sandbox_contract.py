import os

import pytest

REQUIRED_ENV = [
    "DARAJA_CONSUMER_KEY",
    "DARAJA_CONSUMER_SECRET",
    "DARAJA_SHORTCODE",
    "DARAJA_PASSKEY",
    "DARAJA_CALLBACK_URL",
]


def _sandbox_configured():
    return os.environ.get("DARAJA_ENV") == "sandbox" and all(
        os.environ.get(key) for key in REQUIRED_ENV
    )


pytestmark = [
    pytest.mark.external,
    pytest.mark.daraja_sandbox,
    pytest.mark.skipif(
        not _sandbox_configured(),
        reason="Daraja sandbox credentials are not configured.",
    ),
]


def test_daraja_sandbox_environment_is_explicitly_opted_in():
    assert os.environ["DARAJA_ENV"] == "sandbox"
