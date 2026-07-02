param(
    [string]$Image = "postman/newman:6.1.3",
    [string]$Collection = "tests/postman/aesthetic_os_backend_acceptance.postman_collection.json",
    [string]$Environment = "tests/postman/local-docker.postman_environment.json",
    [string]$Report = "tests/postman/reports/newman-local.json",
    [string]$BaseUrl = "",
    [string]$DockerConfigPath = "",
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
    $root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
    return $root.Path
}

function Invoke-Checked {
    param(
        [string]$Exe,
        [string[]]$CommandArgs
    )
    if ($VerboseOutput) {
        Write-Host "RUN $Exe $($CommandArgs -join ' ')"
    }
    & $Exe @CommandArgs
    $exit = $LASTEXITCODE
    if ($exit -ne 0) {
        throw "$Exe failed with exit code $exit"
    }
}

function Initialize-SafeDockerConfig {
    param(
        [string]$RepoRoot,
        [string]$RequestedPath
    )
    if ($RequestedPath) {
        New-Item -ItemType Directory -Force -Path $RequestedPath | Out-Null
        $env:DOCKER_CONFIG = (Resolve-Path $RequestedPath).Path
        Write-Host "DOCKER_CONFIG_MODE=explicit"
        return
    }
    if ($env:DOCKER_CONFIG) {
        Write-Host "DOCKER_CONFIG_MODE=existing"
        return
    }
    $safePath = Join-Path $RepoRoot "reports\ci\docker-config-empty"
    New-Item -ItemType Directory -Force -Path $safePath | Out-Null
    $env:DOCKER_CONFIG = $safePath
    Write-Host "DOCKER_CONFIG_MODE=temporary_empty_local"
}

function Test-DockerDaemonAccess {
    docker version --format "{{.Server.Version}}" | Out-Null
    $exit = $LASTEXITCODE
    if ($exit -ne 0) {
        Write-Host "DOCKER_ACCESS_RESULT=failed"
        Write-Host "DOCKER_ACCESS_DIAGNOSTIC=Unable to reach Docker daemon from this shell. Check Docker Desktop state, Windows docker_engine pipe permissions, and current user access."
        exit $exit
    }
    Write-Host "DOCKER_ACCESS_RESULT=passed"
}

$RepoRoot = Resolve-RepoRoot
Initialize-SafeDockerConfig -RepoRoot $RepoRoot -RequestedPath $DockerConfigPath
Test-DockerDaemonAccess
$CollectionPath = Resolve-Path (Join-Path $RepoRoot $Collection)
$EnvironmentPath = Resolve-Path (Join-Path $RepoRoot $Environment)
$ReportPath = Join-Path $RepoRoot $Report
$ReportDir = Split-Path -Parent $ReportPath
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$newmanArgs = @(
    "run",
    "--rm",
    "--network",
    "host",
    "-v",
    "$($CollectionPath.Path):/etc/newman/collection.json:ro",
    "-v",
    "$($EnvironmentPath.Path):/etc/newman/environment.json:ro",
    "-v",
    "${ReportDir}:/etc/newman/reports:rw",
    $Image,
    "run",
    "/etc/newman/collection.json",
    "-e",
    "/etc/newman/environment.json",
    "--bail",
    "--reporters",
    "cli,json",
    "--reporter-json-export",
    "/etc/newman/reports/$(Split-Path -Leaf $ReportPath)"
)

if ($BaseUrl) {
    $newmanArgs += @("--env-var", "base_url=$BaseUrl")
}

Write-Host "NEWMAN_RUNNER=docker"
Write-Host "NEWMAN_IMAGE=$Image"
Write-Host "NEWMAN_COLLECTION=$Collection"
Write-Host "NEWMAN_ENVIRONMENT=$Environment"
Write-Host "NEWMAN_REPORT=$Report"
Invoke-Checked -Exe "docker" -CommandArgs $newmanArgs
