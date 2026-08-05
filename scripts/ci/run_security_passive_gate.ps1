param(
    [ValidateSet("api", "newman", "frontend", "all-passive")]
    [string]$Mode = "api"
)

$ErrorActionPreference = "Stop"

Write-Host "SECURITY_PASSIVE_GATE_MODE=$Mode"

# API scan profile for web/worker; FE edge when scanning public Nuxt surfaces.
$composeArgs = @("-f", "docker-compose.yml", "-f", "docker-compose.security-scan.yml", "up", "-d", "web", "worker")
if ($Mode -eq "frontend" -or $Mode -eq "all-passive") {
    $composeArgs = @("up", "-d", "web", "worker", "frontend", "frontend-edge")
}
& docker compose @composeArgs
if ($LASTEXITCODE -ne 0) {
    throw "Failed to start compose services for ZAP passive gate."
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

    if ($Mode -eq "frontend" -or $Mode -eq "all-passive") {
        $feReady = $false
        for ($i = 0; $i -lt 60; $i++) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:3000/" -Method GET -TimeoutSec 10 -UseBasicParsing
                if ($response.StatusCode -eq 200) {
                    Write-Host "FRONTEND_EDGE_READY=True"
                    $feReady = $true
                    break
                }
            } catch {
                Start-Sleep -Seconds 3
            }
        }
        if (!$feReady) {
            throw "Frontend edge did not become ready for passive FE scan."
        }
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
