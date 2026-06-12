param(
    [string]$Target = "http://host.docker.internal:8000",
    [int]$SpiderMinutes = 2,
    [int]$MaxMinutes = 8
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ReportDir = Join-Path $RepoRoot "reports\security\zap"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

Write-Host "ZAP_TARGET=$Target"
Write-Host "ZAP_REPORT_DIR=$ReportDir"
Write-Host "ZAP_SPIDER_MINUTES=$SpiderMinutes"
Write-Host "ZAP_MAX_MINUTES=$MaxMinutes"

$DockerArgs = @(
    "run",
    "--rm",
    "-v",
    "${ReportDir}:/zap/wrk/:rw",
    "ghcr.io/zaproxy/zaproxy:stable",
    "zap-baseline.py",
    "-t",
    $Target,
    "-m",
    "$SpiderMinutes",
    "-T",
    "$MaxMinutes",
    "-r",
    "zap-baseline.html",
    "-w",
    "zap-baseline.md",
    "-J",
    "zap-baseline.json"
)

& docker @DockerArgs
$ExitCode = $LASTEXITCODE

Write-Host "ZAP_EXIT_CODE=$ExitCode"
Write-Host "ZAP_HTML_EXISTS=$(Test-Path (Join-Path $ReportDir 'zap-baseline.html'))"
Write-Host "ZAP_MD_EXISTS=$(Test-Path (Join-Path $ReportDir 'zap-baseline.md'))"
Write-Host "ZAP_JSON_EXISTS=$(Test-Path (Join-Path $ReportDir 'zap-baseline.json'))"

exit $ExitCode
