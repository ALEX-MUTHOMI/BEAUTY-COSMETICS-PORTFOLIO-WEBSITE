#!/usr/bin/env pwsh
# Hostile Newman lane (fake providers / local only).
param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$EnvFile = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Collection = Join-Path $RepoRoot "tests\postman\aesthetic_os_hostile_red_team.postman_collection.json"
if (-not $EnvFile) {
    $EnvFile = Join-Path $RepoRoot "tests\postman\local-docker.postman_environment.json"
}
$ReportDir = Join-Path $RepoRoot "tests\postman\reports"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Report = Join-Path $ReportDir "newman-hostile-red-team.json"

$uri = [Uri]$BaseUrl
$allowed = @("localhost", "127.0.0.1", "host.docker.internal")
if ($uri.Scheme -ne "http" -or $allowed -notcontains $uri.Host) {
    throw "Hostile Newman refuses non-local BaseUrl: $BaseUrl"
}

docker run --rm --network host `
  -v "${RepoRoot}:/etc/newman" `
  -w /etc/newman `
  postman/newman:6.1.3 `
  run tests/postman/aesthetic_os_hostile_red_team.postman_collection.json `
  -e tests/postman/local-docker.postman_environment.json `
  --bail `
  --reporters cli,json `
  --reporter-json-export tests/postman/reports/newman-hostile-red-team.json
