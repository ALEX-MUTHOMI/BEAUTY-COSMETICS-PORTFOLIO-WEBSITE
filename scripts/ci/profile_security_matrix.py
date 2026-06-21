"""Run each security test module with an in-process timeout and a compact report."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECURITY_DIR = ROOT / "tests" / "security"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bounded per-file security-suite profiler.")
    parser.add_argument("--per-file-timeout", type=int, default=180)
    parser.add_argument("--reuse-db", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failed = False
    print(f"SECURITY_PROFILE_TIMEOUT_SECONDS={args.per_file_timeout}")
    for path in sorted(SECURITY_DIR.glob("test_*.py")):
        command = [sys.executable, "-m", "pytest", str(path), "-q", "--durations=5", "--maxfail=1"]
        if args.reuse_db:
            command.insert(3, "--reuse-db")
        started = time.monotonic()
        try:
            completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=args.per_file_timeout)
            elapsed = time.monotonic() - started
            status = "passed" if completed.returncode == 0 else f"failed:{completed.returncode}"
            print(f"SECURITY_PROFILE_FILE={path.name}|status={status}|seconds={elapsed:.2f}")
            if completed.returncode:
                print(completed.stdout[-4000:])
                print(completed.stderr[-4000:], file=sys.stderr)
                failed = True
                break
        except subprocess.TimeoutExpired as exc:
            elapsed = time.monotonic() - started
            print(f"SECURITY_PROFILE_FILE={path.name}|status=timeout|seconds={elapsed:.2f}")
            if exc.stdout:
                print(str(exc.stdout)[-4000:])
            failed = True
            break
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
