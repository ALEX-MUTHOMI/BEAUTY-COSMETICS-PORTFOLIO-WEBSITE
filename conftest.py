import pytest


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
