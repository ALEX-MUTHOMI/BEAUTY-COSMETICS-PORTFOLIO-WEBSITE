from pathlib import Path


def test_no_daraja_credentials_are_committed():
    root = Path(__file__).resolve().parents[2]
    credential_names = (
        "DARAJA_CONSUMER_SECRET",
        "DARAJA_PASSKEY",
        "DARAJA_TEST_MSISDN",
    )
    scanned = []
    scan_roots = [
        root / "billing",
        root / "checkout",
        root / "core",
        root / "tests",
        root / "scripts",
        root / ".github",
        root / ".env.example",
        root / "docker-compose.yml",
        root / "pyproject.toml",
        root / "pytest.ini",
    ]
    for scan_root in scan_roots:
        paths = [scan_root] if scan_root.is_file() else scan_root.rglob("*")
        for path in paths:
            if path.is_dir() or ".git" in path.parts or path.suffix in {".pyc", ".sqlite3"}:
                continue
            if path.name in {"poetry.lock"}:
                continue
            if path.name == ".env.example":
                continue
            if path.name == "test_payment_provider_secret_hygiene.py":
                continue
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            scanned.append(path)
            for line in text.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                for token in credential_names:
                    if f"{token}=" not in stripped:
                        continue
                    _, value = stripped.split("=", 1)
                    value = value.strip().strip("\"'")
                    is_placeholder = not value or value.startswith("${") or value.startswith("<")
                    if token == "DARAJA_TEST_MSISDN":
                        is_placeholder = is_placeholder or not value.startswith("254")
                    assert is_placeholder, f"credential-shaped value found in {path}"

    assert scanned
