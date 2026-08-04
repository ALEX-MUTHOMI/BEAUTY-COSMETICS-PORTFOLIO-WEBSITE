import pytest

from scripts.ci.cleanup_test_db_sessions import (
    UnsafeTestDatabaseTarget,
    _assert_safe_test_database_name,
    _derive_test_database_name,
    main,
)


def test_cleanup_test_db_name_derivation_prefers_explicit_test_name():
    settings = {"NAME": "aesthetic_os_db", "TEST": {"NAME": "test_beauty_custom"}}

    assert _derive_test_database_name(settings) == "test_beauty_custom"


def test_cleanup_test_db_name_derivation_defaults_to_test_prefix():
    settings = {"NAME": "aesthetic_os_db"}

    assert _derive_test_database_name(settings) == "test_aesthetic_os_db"


@pytest.mark.parametrize("name", ["aesthetic_os_db", "postgres", "template0", "", "prod"])
def test_cleanup_refuses_non_test_database_names(name):
    with pytest.raises(UnsafeTestDatabaseTarget):
        _assert_safe_test_database_name(name)


@pytest.mark.parametrize("name", ["test_aesthetic_os_db", "beauty_db_test"])
def test_cleanup_allows_only_clear_test_database_names(name):
    _assert_safe_test_database_name(name)


def test_cleanup_main_refuses_destructive_action_without_confirmation(monkeypatch, capsys):
    monkeypatch.setattr(
        "scripts.ci.cleanup_test_db_sessions.load_test_database_target",
        lambda: type("Target", (), {"name": "test_aesthetic_os_db"})(),
    )

    exit_code = main(["--terminate-sessions"])

    output = capsys.readouterr().out
    assert exit_code == 2
    assert "target_database=test_aesthetic_os_db" in output
    assert "explicit confirmation flag required" in output
    assert "password" not in output.lower()
