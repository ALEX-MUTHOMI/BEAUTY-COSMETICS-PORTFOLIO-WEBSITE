import argparse
import json
from collections import Counter
from pathlib import Path

COOKIE_CONTROL_MARKERS = (
    "sessionid",
    "csrftoken",
)

SECRET_MARKERS = (
    "access token",
    "refresh token",
    "consumer secret",
    "passkey",
    "receipt token",
    "checkout_id",
    "ledger_id",
    "storage key",
    "provider payload",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def alerts_from_report(report: dict) -> list[dict]:
    alerts: list[dict] = []
    for site in report.get("site", []) or []:
        alerts.extend(site.get("alerts", []) or [])
    return alerts


def alert_counts(alerts: list[dict]) -> Counter:
    counts: Counter = Counter()
    for alert in alerts:
        risk = str(alert.get("riskdesc", "Unknown")).split(" ", maxsplit=1)[0]
        counts[risk] += 1
    return counts


def observed_urls(alerts: list[dict], urls_file: Path | None) -> set[str]:
    urls: set[str] = set()
    if urls_file and urls_file.exists():
        payload = load_json(urls_file)
        urls.update(str(url) for url in payload.get("urls", []) if isinstance(url, str))
    for alert in alerts:
        for instance in alert.get("instances", []) or []:
            uri = instance.get("uri")
            if uri:
                urls.add(str(uri))
    return urls


def scan_for_markers(paths: list[Path], markers: tuple[str, ...]) -> int:
    hits = 0
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for marker in markers:
            if marker in text:
                hits += 1
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize local ZAP JSON reports without printing sensitive payloads."
    )
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--urls-file", type=Path)
    args = parser.parse_args()

    report = load_json(args.file)
    alerts = alerts_from_report(report)
    counts = alert_counts(alerts)
    urls = observed_urls(alerts, args.urls_file)
    scanned_paths = [args.file, args.urls_file] if args.urls_file else [args.file]
    secret_markers = scan_for_markers(scanned_paths, SECRET_MARKERS)
    cookie_markers = scan_for_markers(scanned_paths, COOKIE_CONTROL_MARKERS)

    print(f"ZAP_SUMMARY_FILE={args.file}")
    print(f"ZAP_ALERTS={len(alerts)}")
    print(f"ZAP_ALERT_RISK_COUNTS={dict(sorted(counts.items()))}")
    print(f"ZAP_OBSERVED_URL_COUNT={len(urls)}")
    print(f"ZAP_SENSITIVE_MARKER_HITS={secret_markers}")
    print(f"ZAP_COOKIE_CONTROL_MARKER_HITS={cookie_markers}")
    for alert in alerts:
        plugin = alert.get("pluginid")
        name = alert.get("alert")
        risk = alert.get("riskdesc")
        instances = len(alert.get("instances", []) or [])
        print(f"ZAP_ALERT={plugin}|{name}|{risk}|instances={instances}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
