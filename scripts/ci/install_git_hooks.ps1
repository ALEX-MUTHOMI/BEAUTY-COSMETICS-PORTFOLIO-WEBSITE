<#
.SYNOPSIS
  Install pre-commit + pre-push hooks so lint cannot reach GitHub Actions.

.DESCRIPTION
  Uses Poetry's pre-commit package and .pre-commit-config.yaml.
  After install:
    - git commit  → format + ruff + secret hygiene + oxlint (staged-relevant)
    - git push    → scripts/ci/local_ci_mirror.ps1 (full lint ladder + vue-tsc)

  One-time:  .\scripts\ci\install_git_hooks.ps1
#>
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    throw "poetry not found on PATH."
}

Write-Host "== Ensuring poetry dev deps (includes pre-commit) =="
poetry install --with dev --no-root
if ($LASTEXITCODE -ne 0) {
    throw "poetry install --with dev failed with exit $LASTEXITCODE"
}

Write-Host "== Installing pre-commit (poetry) =="
poetry run pre-commit install --install-hooks --hook-type pre-commit --hook-type pre-push
if ($LASTEXITCODE -ne 0) {
    throw "pre-commit install failed with exit $LASTEXITCODE"
}

Write-Host ""
Write-Host "GIT_HOOKS_RESULT=installed"
Write-Host "pre-commit: black/isort/ruff/secret_hygiene/oxlint"
Write-Host "pre-push:   local_ci_mirror.ps1 (CI lint ladder + type-check)"
Write-Host ""
Write-Host "Manual full mirror (optional Vitest/build):"
Write-Host "  .\scripts\ci\local_ci_mirror.ps1 -IncludeFrontendTest -IncludeFrontendBuild -IncludeBandit"
