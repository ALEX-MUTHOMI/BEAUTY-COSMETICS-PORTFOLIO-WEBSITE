param(
    [switch]$UseHostNewman,
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"

if ($UseHostNewman) {
    $hostNewman = Get-Command "newman.cmd" -ErrorAction SilentlyContinue
    if ($hostNewman) {
        Write-Host "NEWMAN_RUNNER=host"
        & newman.cmd run tests\postman\beauty_backend_acceptance.postman_collection.json `
            -e tests\postman\local-docker.postman_environment.json `
            --bail `
            --reporters cli,json `
            --reporter-json-export tests\postman\reports\newman-local.json
        if ($LASTEXITCODE -ne 0) {
            throw "host newman.cmd failed with exit code $LASTEXITCODE"
        }
        exit 0
    }
    Write-Host "HOST_NEWMAN_AVAILABLE=False"
    Write-Host "HOST_NEWMAN_FALLBACK=docker"
}

& (Join-Path $PSScriptRoot "run_newman_docker.ps1") -VerboseOutput:$VerboseOutput
if ($LASTEXITCODE -ne 0) {
    throw "Docker Newman runner failed with exit code $LASTEXITCODE"
}

