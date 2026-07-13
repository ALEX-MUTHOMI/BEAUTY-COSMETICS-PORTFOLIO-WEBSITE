#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Authenticated passive ZAP spider for Staff Portal (/api/staff/*).

.DESCRIPTION
  Local HTTP only. Injects sessionid + csrftoken into ZAP baseline spider.
  Does NOT run zap-full-scan / active attack (forbidden for local by ZAP_BASELINE_RUNBOOK).

.EXAMPLE
  .\scripts\security\zap_staff_authenticated_passive.ps1 -SessionId '...' -CsrfToken '...'
#>
param(
    [Parameter(Mandatory = $true)][string]$SessionId,
    [Parameter(Mandatory = $true)][string]$CsrfToken,
    [string]$Target = "http://host.docker.internal:8000",
    [int]$SpiderMinutes = 2,
    [int]$MaxMinutes = 10
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ReportDir = Join-Path $RepoRoot "reports\security\zap\staff-auth"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$uri = [Uri]$Target
$allowed = @("localhost", "127.0.0.1", "host.docker.internal")
if ($uri.Scheme -ne "http" -or $allowed -notcontains $uri.Host -or $uri.Port -ne 8000) {
    throw "Unsafe ZAP target for authenticated passive scan: $Target"
}

$ZapImage = "ghcr.io/zaproxy/zaproxy:stable"
$Container = "aesthetic_os_zap_staff_auth_passive"
docker rm -f $Container 2>$null | Out-Null

# Cookie injection via ZAP CLI replacer / context is brittle across images;
# use baseline with custom headers for authenticated GETs on staff API.
$AjaxTimeout = [Math]::Max(60, $SpiderMinutes * 60)

docker run --rm --name $Container `
  -v "${ReportDir}:/zap/wrk:rw" `
  --add-host=host.docker.internal:host-gateway `
  $ZapImage `
  zap-baseline.py -t "$Target/api/staff/auth/me/" `
  -z "-config replacer.full_list(0).description=staff-session -config replacer.full_list(0).enabled=true -config replacer.full_list(0).matchtype=REQ_HEADER -config replacer.full_list(0).matchstr=Cookie -config replacer.full_list(0).replacement=sessionid=$SessionId;csrftoken=$CsrfToken" `
  -m $MaxMinutes `
  -d `
  -I `
  -r zap-staff-auth-baseline.html `
  -w zap-staff-auth-baseline.md `
  -J zap-staff-auth-baseline.json

Write-Host "Reports: $ReportDir"
