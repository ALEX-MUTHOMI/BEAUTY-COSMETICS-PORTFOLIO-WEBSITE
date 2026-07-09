#!/usr/bin/env python3
"""Emit a markdown CI gate summary for CASS / bookings certification."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _read_newman_summary(path: Path) -> str:
    if not path.is_file():
        return "Newman report: not found"
    payload = json.loads(path.read_text(encoding="utf-8"))
    run = payload.get("run", {})
    stats = run.get("stats", {})
    assertions = stats.get("assertions", {})
    requests = stats.get("requests", {})
    return (
        f"Newman: {requests.get('total', 0)} requests, "
        f"{assertions.get('total', 0)} assertions, "
        f"{assertions.get('failed', 0)} failed"
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    reports_dir = repo_root / "reports" / "ci"
    reports_dir.mkdir(parents=True, exist_ok=True)

    gate_name = sys.argv[1] if len(sys.argv) > 1 else "cass-certification"
    status = sys.argv[2] if len(sys.argv) > 2 else "passed"
    notes = sys.argv[3:] if len(sys.argv) > 3 else []

    newman_line = _read_newman_summary(reports_dir / "newman" / "newman-local.json")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = [
        f"# {gate_name}",
        "",
        f"- generated_utc: {now}",
        f"- status: **{status}**",
        "- cass_policy: Option A (type-level only)",
        "",
        "## Evidence",
        "",
        f"- {newman_line}",
    ]
    for note in notes:
        lines.append(f"- {note}")

    output = reports_dir / f"{gate_name}.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"GATE_REPORT={output}")
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
