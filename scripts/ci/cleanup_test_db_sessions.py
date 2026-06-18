import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path6

from psycopg2 import sql

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@dataclass(frozen=True)
class TestDatabaseTarget:
    engine: str
    name: str
    maintenance_name: str
    user: str
    password: str
    host: str
    port: str


class UnsafeTestDatabaseTarget(RuntimeError):
    pass


def _setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    import django

    django.setup()


def _derive_test_database_name(database_settings: dict) -> str:
    explicit_name = (database_settings.get("TEST") or {}).get("NAME")
    if explicit_name:
        return str(explicit_name)
    return f"test_{database_settings['NAME']}"


def _assert_safe_test_database_name(name: str) -> None:
    normalized = str(name or "").strip().lower()
    if normalized in {"", "postgres", "template0", "template1"}:
        raise UnsafeTestDatabaseTarget("Refusing to target a system or empty database name.")
    if not (normalized.startswith("test_") or normalized.endswith("_test")):
        raise UnsafeTestDatabaseTarget("Refusing to target a database that is not clearly a test database.")


def load_test_database_target() -> TestDatabaseTarget:
    _setup_django()
    from django.conf import settings

    database_settings = settings.DATABASES["default"]
    engine = database_settings.get("ENGINE", "")
    if "postgresql" not in engine:
        raise UnsafeTestDatabaseTarget("Only PostgreSQL test database cleanup is supported.")

    name = _derive_test_database_name(database_settings)
    _assert_safe_test_database_name(name)
    return TestDatabaseTarget(
        engine=engine,
        name=name,
        maintenance_name=database_settings.get("MAINTENANCE_DB", "postgres"),
        user=database_settings.get("USER", ""),
        password=database_settings.get("PASSWORD", ""),
        host=database_settings.get("HOST", ""),
        port=str(database_settings.get("PORT", "5432")),
    )


def _connect(target: TestDatabaseTarget):
    import psycopg2

    return psycopg2.connect(
        dbname=target.maintenance_name,
        user=target.user,
        password=target.password,
        host=target.host,
        port=target.port,
    )


def terminate_sessions(target: TestDatabaseTarget) -> int:
    with _connect(target) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM pg_stat_activity
                WHERE datname = %s AND pid != pg_backend_pid()
                """,
                [target.name],
            )
            before = int(cursor.fetchone()[0])
            cursor.execute(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid != pg_backend_pid()
                """,
                [target.name],
            )
    return before


def drop_test_database(target: TestDatabaseTarget) -> None:
    with _connect(target) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(target.name)))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safely clean stale Django PostgreSQL test database sessions.")
    parser.add_argument("--terminate-sessions", action="store_true")
    parser.add_argument("--drop-test-db", action="store_true")
    parser.add_argument(
        "--yes-i-understand-this-targets-only-the-test-db",
        action="store_true",
        help="Required for any destructive action.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    target = load_test_database_target()
    print(f"target_database={target.name}")
    print("target_is_test_database=True")
    if not args.terminate_sessions and not args.drop_test_db:
        print("dry_run=True")
        print("actions=none")
        return 0
    if not args.yes_i_understand_this_targets_only_the_test_db:
        print("refused=True")
        print("reason=explicit confirmation flag required")
        return 2
    if args.terminate_sessions:
        terminated = terminate_sessions(target)
        print(f"terminated_session_count={terminated}")
    if args.drop_test_db:
        terminate_sessions(target)
        drop_test_database(target)
        print("dropped_test_database=True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
