param(
    [ValidateSet("health", "root", "api", "newman", "all-passive")]
    [string]$Mode = "health",
    [string]$Target = "",
    [int]$SpiderMinutes = 2,
    [int]$MaxMinutes = 8,
    [int]$ZapReadySeconds = 300,
    [int]$PassiveDrainSeconds = 120,
    [int]$ReportExportSeconds = 90,
    [switch]$StrictExitCodes
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ZapRoot = Join-Path $RepoRoot "reports\security\zap"
$PostmanRoot = Join-Path $RepoRoot "tests\postman"
$ZapImage = "ghcr.io/zaproxy/zaproxy:stable"
$NewmanImage = "postman/newman:6.1.3"
$ZapNewmanContainer = "aesthetic_os_zap_passive_newman"
$NewmanThroughZapContainer = "aesthetic_os_newman_through_zap"

function Test-SafeLocalTarget {
    param([string]$Url)
    $uri = [Uri]$Url
    $allowedHosts = @("localhost", "127.0.0.1", "host.docker.internal")
    if ($uri.Scheme -ne "http") {
        throw "Unsafe ZAP target scheme for local passive scan: $($uri.Scheme)"
    }
    if ($allowedHosts -notcontains $uri.Host) {
        throw "Unsafe ZAP target host for local passive scan: $($uri.Host)"
    }
    if ($uri.Port -ne 8000) {
        throw "Unsafe ZAP target port for local passive scan: $($uri.Port)"
    }
}

function New-ReportDir {
    param([string]$Name)
    $dir = Join-Path $ZapRoot $Name
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $keep = Join-Path $dir ".gitkeep"
    if (!(Test-Path $keep)) {
        New-Item -ItemType File -Force -Path $keep | Out-Null
    }
    return $dir
}

function Remove-ProjectScannerContainer {
    param([string]$Name)
    if ([string]::IsNullOrWhiteSpace($Name)) {
        throw "Refusing to remove scanner container with empty name."
    }
    if (!$Name.StartsWith("aesthetic_os_")) {
        throw "Refusing to remove non-project scanner container: $Name"
    }
    $existing = & docker ps -a --filter "name=^$Name$" --format "{{.Names}}"
    if ($existing -contains $Name) {
        & docker rm -f $Name | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "ZAP_CLEANUP_FAILED"
        }
    }
}

function Complete-ZapExit {
    param([int]$Code)
    if ($Code -eq 0) {
        return 0
    }
    if ($Code -eq 2) {
        if ($StrictExitCodes) {
            return 2
        }
        return 0
    }
    return $Code
}

function Assert-Artifacts {
    param(
        [string]$ReportDir,
        [string]$Prefix
    )
    $html = Test-Path (Join-Path $ReportDir "$Prefix.html")
    $md = Test-Path (Join-Path $ReportDir "$Prefix.md")
    $json = Test-Path (Join-Path $ReportDir "$Prefix.json")
    Write-Host "ZAP_HTML_EXISTS=$html"
    Write-Host "ZAP_MD_EXISTS=$md"
    Write-Host "ZAP_JSON_EXISTS=$json"
    if (!$html -or !$md -or !$json) {
        throw "ZAP artifact generation failed for $Prefix"
    }
    foreach ($path in @(
        (Join-Path $ReportDir "$Prefix.html"),
        (Join-Path $ReportDir "$Prefix.md"),
        (Join-Path $ReportDir "$Prefix.json")
    )) {
        if ((Get-Item $path).Length -le 0) {
            throw "ZAP artifact is empty: $path"
        }
    }
}

function Invoke-ZapBaseline {
    param(
        [string]$Name,
        [string]$Url,
        [int]$Spider,
        [int]$Max,
        [string]$Prefix
    )
    Test-SafeLocalTarget $Url
    $reportDir = New-ReportDir $Name
    Write-Host "ZAP_MODE=$Name"
    Write-Host "ZAP_TARGET=$Url"
    Write-Host "ZAP_REPORT_DIR=$reportDir"
    Write-Host "ZAP_SPIDER_MINUTES=$Spider"
    Write-Host "ZAP_MAX_MINUTES=$Max"

    $dockerArgs = @(
        "run",
        "--rm",
        "-v",
        "${reportDir}:/zap/wrk/:rw",
        $ZapImage,
        "zap-baseline.py",
        "-t",
        $Url,
        "-m",
        "$Spider",
        "-T",
        "$Max",
        "-r",
        "$Prefix.html",
        "-w",
        "$Prefix.md",
        "-J",
        "$Prefix.json"
    )
    & docker @dockerArgs | ForEach-Object { Write-Host $_ }
    $zapExit = $LASTEXITCODE
    Write-Host "ZAP_EXIT_CODE=$zapExit"
    Assert-Artifacts -ReportDir $reportDir -Prefix $Prefix
    & python (Join-Path $PSScriptRoot "zap_summarize_reports.py") --file (Join-Path $reportDir "$Prefix.json") | ForEach-Object { Write-Host $_ }
    return (Complete-ZapExit $zapExit)
}

function Invoke-ZapApiScan {
    param(
        [string]$Name,
        [string]$SchemaUrl,
        [int]$Max,
        [string]$Prefix
    )
    Test-SafeLocalTarget $SchemaUrl
    $reportDir = New-ReportDir $Name
    Write-Host "ZAP_MODE=$Name"
    Write-Host "ZAP_TARGET=$SchemaUrl"
    Write-Host "ZAP_API_SAFE_MODE=True"
    Write-Host "ZAP_REPORT_DIR=$reportDir"
    Write-Host "ZAP_MAX_MINUTES=$Max"

    $dockerArgs = @(
        "run",
        "--rm",
        "-v",
        "${reportDir}:/zap/wrk/:rw",
        $ZapImage,
        "zap-api-scan.py",
        "-S",
        "-t",
        $SchemaUrl,
        "-f",
        "openapi",
        "-T",
        "$Max",
        "-r",
        "$Prefix.html",
        "-w",
        "$Prefix.md",
        "-J",
        "$Prefix.json"
    )
    & docker @dockerArgs | ForEach-Object { Write-Host $_ }
    $zapExit = $LASTEXITCODE
    Write-Host "ZAP_EXIT_CODE=$zapExit"
    Assert-Artifacts -ReportDir $reportDir -Prefix $Prefix
    & python (Join-Path $PSScriptRoot "zap_summarize_reports.py") --file (Join-Path $reportDir "$Prefix.json") | ForEach-Object { Write-Host $_ }
    return (Complete-ZapExit $zapExit)
}

function Test-OpenApiSchema {
    $schemaUrl = "http://localhost:8000/api/schema/"
    try {
        $response = Invoke-WebRequest -Uri $schemaUrl -Method GET -TimeoutSec 10 -UseBasicParsing
        return ($response.StatusCode -eq 200)
    } catch {
        return $false
    }
}

function Invoke-ZapApiMode {
    if (!(Test-OpenApiSchema)) {
        $reportDir = New-ReportDir "api"
        $deferred = Join-Path $reportDir "zap-api-baseline.deferred.txt"
        Set-Content -Path $deferred -Value "Deferred: no reachable local OpenAPI schema endpoint was found." -Encoding UTF8
        Write-Host "ZAP_MODE=api"
        Write-Host "ZAP_API_DEFERRED=True"
        Write-Host "ZAP_API_DEFERRED_REASON=no reachable local OpenAPI schema endpoint"
        return 0
    }
    return Invoke-ZapApiScan -Name "api" -SchemaUrl "http://host.docker.internal:8000/api/schema/" -Max $MaxMinutes -Prefix "zap-api-baseline"
}

function Test-ZapApiReady {
    param([string]$ProxyApi)
    try {
        $response = Invoke-WebRequest -Uri "$ProxyApi/JSON/core/view/version/" -Method GET -TimeoutSec 5 -UseBasicParsing
        return $response.StatusCode -eq 200
    } catch {
        if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
            $raw = & curl.exe -s -m 5 "$ProxyApi/JSON/core/view/version/"
            return [bool]($raw -match '"version"')
        }
        return $false
    }
}

function Wait-ZapProxy {
    param(
        [string]$Url,
        [string]$ContainerName = ""
    )
    $deadline = (Get-Date).AddSeconds($ZapReadySeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-ZapApiReady -ProxyApi $Url) {
            Write-Host "ZAP_READY=True"
            return
        }
        Start-Sleep -Seconds 2
    }
    if ($ContainerName) {
        Write-Host "ZAP_READY_DIAGNOSTIC_LOG_TAIL=True"
        & docker logs --tail=120 $ContainerName 2>$null | ForEach-Object { Write-Host $_ }
    }
    throw "ZAP_READY_TIMEOUT"
}

function Wait-ZapPassiveDrain {
    param([string]$ProxyApi)
    $deadline = (Get-Date).AddSeconds($PassiveDrainSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri "$ProxyApi/JSON/pscan/view/recordsToScan/" -Method GET -TimeoutSec 5 -UseBasicParsing
            $payload = $response.Content | ConvertFrom-Json
            $remaining = [int]$payload.recordsToScan
            Write-Host "ZAP_PASSIVE_RECORDS_TO_SCAN=$remaining"
            if ($remaining -eq 0) {
                return
            }
        } catch {
            Write-Host "ZAP_PASSIVE_DRAIN_POLL_FAILED=True"
        }
        Start-Sleep -Seconds 2
    }
    throw "PASSIVE_DRAIN_TIMEOUT"
}

function Save-ZapProxyReport {
    param(
        [string]$ProxyApi,
        [string]$ReportDir,
        [string]$Prefix
    )
    Invoke-WebRequest -Uri "$ProxyApi/OTHER/core/other/htmlreport/" -OutFile (Join-Path $ReportDir "$Prefix.html") -TimeoutSec $ReportExportSeconds -UseBasicParsing
    Invoke-WebRequest -Uri "$ProxyApi/OTHER/core/other/mdreport/" -OutFile (Join-Path $ReportDir "$Prefix.md") -TimeoutSec $ReportExportSeconds -UseBasicParsing
    Invoke-WebRequest -Uri "$ProxyApi/OTHER/core/other/jsonreport/" -OutFile (Join-Path $ReportDir "$Prefix.json") -TimeoutSec $ReportExportSeconds -UseBasicParsing
    Invoke-WebRequest -Uri "$ProxyApi/JSON/core/view/urls/" -OutFile (Join-Path $ReportDir "$Prefix.urls.json") -TimeoutSec $ReportExportSeconds -UseBasicParsing
}

function Invoke-NewmanThroughZap {
    $reportDir = New-ReportDir "newman"
    $prefix = "zap-newman-passive"
    $proxyPort = 8090
    $proxyApi = "http://localhost:$proxyPort"
    $postmanPath = (Resolve-Path $PostmanRoot).Path
    $zapContainerName = $ZapNewmanContainer
    $newmanContainerName = $NewmanThroughZapContainer

    Write-Host "ZAP_MODE=newman"
    Write-Host "ZAP_PROXY_PORT=$proxyPort"
    Write-Host "ZAP_REPORT_DIR=$reportDir"
    Write-Host "ZAP_CONTAINER=$zapContainerName"
    Write-Host "NEWMAN_CONTAINER=$newmanContainerName"

    Remove-ProjectScannerContainer -Name $zapContainerName
    Remove-ProjectScannerContainer -Name $newmanContainerName

    # Join the compose network so ZAP can reach Django as `web:8000` (host.docker.internal
    # through a nested proxy returns 502 on GitHub Actions Linux runners).
    $composeNetwork = "aesthetic_os_isolated_network"
    $targetBaseUrl = "http://web:8000"
    Write-Host "ZAP_COMPOSE_NETWORK=$composeNetwork"
    Write-Host "ZAP_TARGET_BASE_URL=$targetBaseUrl"

    & docker run -d `
        --name $zapContainerName `
        --network $composeNetwork `
        -p "${proxyPort}:8090" `
        -v "${reportDir}:/zap/wrk/:rw" `
        $ZapImage `
        zap.sh -daemon -host 0.0.0.0 -port 8090 `
        -config api.disablekey=true `
        -config api.addrs.addr.name=.* `
        -config api.addrs.addr.regex=true `
        -config network.connection.dnsTtlSuccessfulQueries=-1 `
        -config network.connection.timeoutInSecs=120 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "ZAP_START_FAILED"
    }
    try {
        Wait-ZapProxy -Url $proxyApi -ContainerName $zapContainerName
        # Write Newman JSON into the ZAP report dir (writable mount), not the read-only Postman tree.
        $newmanReportHost = Join-Path $reportDir "newman-through-zap.json"
        $newmanArgs = @(
            "run",
            "--rm",
            "--name",
            $newmanContainerName,
            "--network",
            $composeNetwork,
            "-e",
            "HTTP_PROXY=http://${zapContainerName}:8090",
            "-e",
            "HTTPS_PROXY=http://${zapContainerName}:8090",
            "-e",
            "NO_PROXY=localhost,127.0.0.1",
            "-v",
            "${postmanPath}:/etc/newman:ro",
            "-v",
            "${reportDir}:/zap/wrk/:rw",
            $NewmanImage,
            "run",
            "/etc/newman/aesthetic_os_backend_acceptance.postman_collection.json",
            "-e",
            "/etc/newman/local-docker.postman_environment.json",
            "--env-var",
            "base_url=$targetBaseUrl",
            "--timeout",
            "300000",
            "--timeout-request",
            "60000",
            "--bail",
            "--reporters",
            "cli,json",
            "--reporter-json-export",
            "/zap/wrk/newman-through-zap.json"
        )
        Write-Host "NEWMAN_THROUGH_ZAP_REPORT=$newmanReportHost"
        & docker @newmanArgs | ForEach-Object { Write-Host $_ }
        $newmanExit = $LASTEXITCODE
        Write-Host "NEWMAN_EXIT_CODE=$newmanExit"
        Wait-ZapPassiveDrain -ProxyApi $proxyApi
        Save-ZapProxyReport -ProxyApi $proxyApi -ReportDir $reportDir -Prefix $prefix
        Assert-Artifacts -ReportDir $reportDir -Prefix $prefix
        & python (Join-Path $PSScriptRoot "zap_summarize_reports.py") --file (Join-Path $reportDir "$prefix.json") --urls-file (Join-Path $reportDir "$prefix.urls.json") | ForEach-Object { Write-Host $_ }
        if ($newmanExit -ne 0) {
            throw "Newman-through-ZAP failed"
        }
        return 0
    } finally {
        Remove-ProjectScannerContainer -Name $newmanContainerName
        Remove-ProjectScannerContainer -Name $zapContainerName
    }
}

$exitCodes = @()
if ($Mode -eq "health" -or $Mode -eq "all-passive") {
    $url = if ($Target) { $Target } else { "http://host.docker.internal:8000/health/" }
    $exitCodes += Invoke-ZapBaseline -Name "health" -Url $url -Spider $SpiderMinutes -Max $MaxMinutes -Prefix "zap-health-baseline"
}
if ($Mode -eq "root" -or $Mode -eq "all-passive") {
    $url = if ($Target -and $Mode -eq "root") { $Target } else { "http://host.docker.internal:8000/" }
    $exitCodes += Invoke-ZapBaseline -Name "root" -Url $url -Spider $SpiderMinutes -Max $MaxMinutes -Prefix "zap-root-baseline"
}
if ($Mode -eq "api" -or $Mode -eq "all-passive") {
    $exitCodes += Invoke-ZapApiMode
}
if ($Mode -eq "newman" -or $Mode -eq "all-passive") {
    $exitCodes += Invoke-NewmanThroughZap
}

if (($exitCodes | Where-Object { $_ -ne 0 } | Measure-Object).Count -gt 0) {
    exit (($exitCodes | Where-Object { $_ -ne 0 } | Select-Object -First 1))
}
exit 0
