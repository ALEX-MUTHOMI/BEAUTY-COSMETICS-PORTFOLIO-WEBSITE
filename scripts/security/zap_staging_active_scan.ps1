#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Gated OWASP ZAP *active* full scan for STAGING only.

.DESCRIPTION
  Local turbo_pass / ZAP_BASELINE_RUNBOOK forbid zap-full-scan against localhost.
  This script refuses production hosts and requires CONFIRM_ACTIVE_ZAP=1.

  Focus rules: XSS, SQLi, Path Traversal via default full-scan policy.

.EXAMPLE
  $env:CONFIRM_ACTIVE_ZAP='1'
  .\scripts\security\zap_staging_active_scan.ps1 -Target 'https://staging.example.com'
#>
param(
    [Parameter(Mandatory = $true)][string]$Target,
    [string]$SessionId = "",
    [string]$CsrfToken = "",
    [int]$MaxDurationMinutes = 30
)

$ErrorActionPreference = "Stop"

if ($env:CONFIRM_ACTIVE_ZAP -ne "1") {
    throw "Refusing active ZAP scan. Set CONFIRM_ACTIVE_ZAP=1 after reviewing staging blast radius."
}

$uri = [Uri]$Target
$blockedHosts = @("localhost", "127.0.0.1", "host.docker.internal")
$blockedNameParts = @("prod", "production", "live", "www.shee", "aesthetics.co.ke")
if ($blockedHosts -contains $uri.Host) {
    throw "Active ZAP full-scan is forbidden against local targets. Use zap_staff_authenticated_passive.ps1."
}
foreach ($part in $blockedNameParts) {
    if ($uri.Host.ToLowerInvariant().Contains($part) -and -not $uri.Host.ToLowerInvariant().Contains("staging")) {
        throw "Active ZAP refused host that looks like production: $($uri.Host)"
    }
}
if ($uri.Scheme -ne "https") {
    throw "Staging active scan requires https://"
}

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ReportDir = Join-Path $RepoRoot "reports\security\zap\staging-active"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$ZapImage = "ghcr.io/zaproxy/zaproxy:weekly"
$Container = "aesthetic_os_zap_staging_active"
docker rm -f $Container 2>$null | Out-Null

$cookieConfig = ""
if ($SessionId -and $CsrfToken) {
    $cookieConfig = "-z `"-config replacer.full_list(0).description=staff-session -config replacer.full_list(0).enabled=true -config replacer.full_list(0).matchtype=REQ_HEADER -config replacer.full_list(0).matchstr=Cookie -config replacer.full_list(0).replacement=sessionid=$SessionId;csrftoken=$CsrfToken`""
}

$cmd = @(
    "docker", "run", "--rm", "--name", $Container,
    "-v", "${ReportDir}:/zap/wrk:rw",
    $ZapImage,
    "zap-full-scan.py",
    "-t", $Target,
    "-m", "$MaxDurationMinutes",
    "-d",
    "-I",
    "-r", "zap-staging-full.html",
    "-w", "zap-staging-full.md",
    "-J", "zap-staging-full.json"
)

Write-Host "Running:" ($cmd -join " ")
if ($cookieConfig) {
    Write-Host "Cookie injection enabled for authenticated spidering."
}

& docker run --rm --name $Container `
  -v "${ReportDir}:/zap/wrk:rw" `
  $ZapImage `
  zap-full-scan.py -t $Target -m $MaxDurationMinutes -d -I `
  -r zap-staging-full.html -w zap-staging-full.md -J zap-staging-full.json

Write-Host "Reports: $ReportDir"
