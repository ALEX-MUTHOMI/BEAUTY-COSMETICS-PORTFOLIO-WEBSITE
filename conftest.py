import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-external",
        action="store_true",
        default=False,
        help="Run opt-in external provider contract tests.",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-external"):
        return
    skip_external = pytest.mark.skip(
        reason="external provider tests require --run-external"
    )
    for item in items:
        if "external" in item.keywords:
            item.add_marker(skip_external)
