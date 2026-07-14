#!/usr/bin/env pwsh
# Hostile Newman lane (fake providers / local only).
param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$EnvFile = "",
    [string]$Image = "postman/newman:6.1.3"
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

# Same seed baseline as acceptance Newman so availability/hold paths resolve.
docker compose exec -T web poetry run python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "migrate exit=$LASTEXITCODE - retrying once after brief wait"
    Start-Sleep -Seconds 5
    docker compose exec -T web poetry run python manage.py migrate --noinput
}
if ($LASTEXITCODE -ne 0) { throw "migrate failed" }
docker compose exec -T web poetry run python manage.py seed_api_acceptance_data
if ($LASTEXITCODE -ne 0) { throw "seed_api_acceptance_data failed" }
docker compose exec -T web poetry run python manage.py seed_marketing_catalog
if ($LASTEXITCODE -ne 0) { throw "seed_marketing_catalog failed" }

# Holds send X-Forwarded-Proto: https (parity with acceptance Newman); CSRF referer must be https.
$csrfReferer = ($BaseUrl -replace '^http://', 'https://') + '/api/csrf/'
Write-Host "HOSTILE_NEWMAN_BASE_URL=$BaseUrl"
Write-Host "HOSTILE_NEWMAN_CSRF_REFERER=$csrfReferer"

docker run --rm --network host `
  -v "${RepoRoot}:/etc/newman" `
  -w /etc/newman `
  $Image `
  run tests/postman/aesthetic_os_hostile_red_team.postman_collection.json `
  -e tests/postman/local-docker.postman_environment.json `
  --env-var "base_url=$BaseUrl" `
  --env-var "csrf_referer=$csrfReferer" `
  --bail `
  --reporters cli,json `
  --reporter-json-export tests/postman/reports/newman-hostile-red-team.json

exit $LASTEXITCODE
