#!/usr/bin/env python3
"""
Secret Hygiene Scanner
CI fail-safe script to scan Git-tracked files for hardcoded secrets,
ensuring ZERO leakage in public logs, with false-positive exemptions.
"""

import os
import re
import subprocess
import sys

# Regex rules for credentials detection
SECRET_RULES = {
    "Stripe/M-Pesa API Key": re.compile(r"(?:sk_live|rk_live)_[a-zA-Z0-9]{24,}"),
    "AWS Access Key ID": re.compile(r"([^A-Z0-9]|^)(AKIA[A-Z0-9]{16})([^A-Z0-9]|$)"),
    "AWS Secret Access Key": re.compile(
        r"(?i)aws_secret_access_key\s*=\s*['\"]([a-zA-Z0-9/+=]{40})['\"]"
    ),
    "Generic API Key / Secret / Private Key": re.compile(
        r"(?i)(?:api_key|api_token|secret_key|private_key|auth_token)\s*=\s*['\"]([a-zA-Z0-9_\-\.\:\/\@]{16,})['\"]"
    ),
    "Database Password URI": re.compile(
        r"postgres(?:ql)?://[a-zA-Z0-9_]+:(?P<password>[^@\s]+)@[a-zA-Z0-9_\.\-]+:[0-9]+/[a-zA-Z0-9_\-]+"
    ),
    "Django Hardcoded SECRET_KEY": re.compile(
        r"^SECRET_KEY\s*=\s*['\"](?P<key>[a-zA-Z0-9!@#$%\^&\*\(\)_\+\-=\[\]\{\};':\",\./<>\?]{30,})['\"]"
    ),
}

# Exclusion markers - Inline ignore comments
IGNORE_MARKERS = ["# nosec", "# pragma: allowlist secret"]

# Files or folders to explicitly skip (e.g. this script itself, lock files, templates)
EXCLUDED_PATTERNS = [
    r"scripts/ci/secret_hygiene.py",
    r"poetry.lock",
    r"package-lock.json",
    r"\.git/",
    r"\.env\.example",
]


def should_exclude(file_path):
    """Check if the file path is explicitly excluded from scans."""
    return any(re.search(pattern, file_path) for pattern in EXCLUDED_PATTERNS)


def get_git_tracked_files():
    """Retrieve all files tracked by Git to prevent checking heavy build directories."""
    try:
        result = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[-] Git command failed or Git is not initialized: {e}")
        # Fallback to scanning all workspace files if git is not available
        files = []
        for root, _, filenames in os.walk("."):
            for filename in filenames:
                path = os.path.relpath(os.path.join(root, filename), ".")
                files.append(path)
        return files


def scan_file(file_path):
    """Scan a file for hardcoded secrets, returning a list of detections."""
    detections = []

    if should_exclude(file_path):
        return detections

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.strip()

                # Check for inline bypass markers
                if any(marker in clean_line for marker in IGNORE_MARKERS):
                    continue

                for rule_name, pattern in SECRET_RULES.items():
                    match = pattern.search(clean_line)
                    if match:
                        # Extra validation for Django SECRET_KEY rule to avoid false flagging env references
                        if (
                            rule_name == "Generic API Key / Secret / Private Key"
                            and any(
                                env_call in clean_line
                                for env_call in [
                                    "environ",
                                    "env.",
                                    "config(",
                                    "os.getenv",
                                ]
                            )
                        ):
                            # Ignore env loader calls (e.g. os.environ, env.str, config('...'))
                            continue

                        if rule_name == "Django Hardcoded SECRET_KEY" and (
                            "os.environ" in clean_line
                            or "env(" in clean_line
                            or "get_env" in clean_line
                        ):
                            # Ignore if we are looking up from an env variable
                            continue

                        detections.append(
                            {"file": file_path, "line": line_num, "rule": rule_name}
                        )
    except Exception:
        # Gracefully handle file reading errors (e.g., binary files missed by git filtering)
        pass

    return detections


def main():
    print("[*] Initializing Secret Hygiene Scanner...")
    tracked_files = get_git_tracked_files()
    total_files_scanned = 0
    all_detections = []

    for file_path in tracked_files:
        if os.path.isfile(file_path):
            total_files_scanned += 1
            detections = scan_file(file_path)
            all_detections.extend(detections)

    print(f"[*] Scanned {total_files_scanned} files.")

    if all_detections:
        print("\n[!] CRITICAL: Hardcoded secrets detected in repository!")
        print("[!] SECURITY WARNING: Secrets must never be committed to git.")
        print("-" * 80)

        for det in all_detections:
            # STRICT OUTPUT REDACTION: Absolutely NEVER print the matched secret value.
            # Only print the file, line, and rule triggered.
            print(f"MATCH TRIGGERED: [{det['rule']}]")
            print(f"  File: {det['file']}")
            print(f"  Line: {det['line']}")
            print("-" * 80)

        print(
            "\n[!] Remediate by moving credentials to an external environment (.env) configuration."
        )
        print(
            "[!] To bypass false positives, append '# nosec' or '# pragma: allowlist secret' to the offending line."
        )
        sys.exit(1)

    print("[+] Secret hygiene validation passed successfully. No secrets exposed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
