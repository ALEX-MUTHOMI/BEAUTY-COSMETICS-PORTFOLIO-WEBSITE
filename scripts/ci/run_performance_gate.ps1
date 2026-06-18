param(
    [ValidateSet("smoke", "standard", "load", "latency")]
    [string]$Mode = "standard",
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param([string]$Command)
    Write-Host "RUN $Command"
    powershell -NoProfile -ExecutionPolicy Bypass -Command $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE"
    }
}

switch ($Mode) {
    "smoke" {
        Invoke-Checked "docker compose exec -T web poetry run pytest tests/latency/test_payment_spinner_timeout.py tests/load/test_redis_failure_safety.py -q --durations=10"
    }
    "load" {
        Invoke-Checked "docker compose exec -T web poetry run pytest tests/load -q --durations=25"
    }
    "latency" {
        Invoke-Checked "docker compose exec -T web poetry run pytest tests/latency -q --durations=25"
    }
    "standard" {
        Invoke-Checked "docker compose exec -T web poetry run pytest tests/load -q --durations=25"
        Invoke-Checked "docker compose exec -T web poetry run pytest tests/latency -q --durations=25"
    }
}

