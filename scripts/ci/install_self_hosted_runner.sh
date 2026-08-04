#!/usr/bin/env bash
# Install / configure GitHub Actions self-hosted runner for AestheticOS (Linux).
# Prefer WSL2 Ubuntu with Docker Desktop integration. See docs/ops/SELF_HOSTED_RUNNER.md.
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/ALEX-MUTHOMI/aesthetic-os}"
RUNNER_NAME="${RUNNER_NAME:-aesthetic-os-wsl}"
RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,linux,aesthetic-os}"
RUNNER_DIR="${RUNNER_DIR:-$HOME/actions-runner}"
RUNNER_VERSION="${RUNNER_VERSION:-2.328.0}"

if [[ -z "${RUNNER_TOKEN:-}" ]]; then
  echo "RUNNER_TOKEN is required (repo registration token; never commit it)." >&2
  echo "Create with: gh api -X POST repos/ALEX-MUTHOMI/aesthetic-os/actions/runners/registration-token --jq .token" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found on PATH. Enable Docker Desktop WSL integration for this distro." >&2
  exit 1
fi
docker version >/dev/null

mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

if [[ ! -f ./config.sh ]]; then
  curl -fsSL -o actions-runner-linux-x64.tar.gz \
    "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
  tar xzf ./actions-runner-linux-x64.tar.gz
  rm -f ./actions-runner-linux-x64.tar.gz
fi

# Optional: PowerShell for ZAP passive gate scripts on Linux runners.
if ! command -v pwsh >/dev/null 2>&1; then
  echo "NOTE: pwsh not installed. zap-passive-newman needs PowerShell 7 — see SELF_HOSTED_RUNNER.md"
fi

./config.sh --unattended \
  --url "$REPO_URL" \
  --token "$RUNNER_TOKEN" \
  --name "$RUNNER_NAME" \
  --labels "$RUNNER_LABELS" \
  --work "_work" \
  --replace

echo "Configured. Start with: cd $RUNNER_DIR && ./run.sh"
echo "Or install service: sudo ./svc.sh install && sudo ./svc.sh start"
