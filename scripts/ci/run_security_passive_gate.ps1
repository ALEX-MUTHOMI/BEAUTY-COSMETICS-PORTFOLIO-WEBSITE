param(
    [ValidateSet("api", "newman", "all-passive")]
    [string]$Mode = "api"
)

$ErrorActionPreference = "Stop"

Write-Host "SECURITY_PASSIVE_GATE_MODE=$Mode"
docker compose -f docker-compose.yml -f docker-compose.security-scan.yml up -d web worker
if ($LASTEXITCODE -ne 0) {
    throw "Failed to enable security-scan profile."
}

try {
    $schemaReady = $false
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/api/schema/" -Method GET -TimeoutSec 20 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "OPENAPI_SCHEMA_READY=True"
                $schemaReady = $true
                break
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    if (($Mode -eq "api" -or $Mode -eq "all-passive") -and !$schemaReady) {
        throw "OpenAPI schema did not become ready for passive API scan."
    }
    # Prefer pwsh (CI / PS7); fall back to Windows PowerShell 5.1 when pwsh is absent.
    $zapScript = Join-Path $PSScriptRoot "..\security\zap_baseline_local.ps1"
    $shell = Get-Command pwsh -ErrorAction SilentlyContinue
    if (-not $shell) {
        $shell = Get-Command powershell -ErrorAction SilentlyContinue
    }
    if (-not $shell) {
        throw "Neither pwsh nor powershell found on PATH for ZAP passive gate."
    }
    & $shell.Source -NoProfile -ExecutionPolicy Bypass -File $zapScript -Mode $Mode
    if ($LASTEXITCODE -ne 0) {
        throw "ZAP passive gate failed with exit code $LASTEXITCODE"
    }
} finally {
    docker compose up -d web worker
    if ($LASTEXITCODE -ne 0) {
        Write-Host "DEFAULT_RUNTIME_RESTORE_FAILED=True"
    }
}
