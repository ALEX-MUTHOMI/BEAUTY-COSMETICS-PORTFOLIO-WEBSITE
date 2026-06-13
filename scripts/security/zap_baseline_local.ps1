param(
    [ValidateSet("health", "root", "api", "newman", "all-passive")]
    [string]$Mode = "health",
    [string]$Target = "",
    [int]$SpiderMinutes = 2,
    [int]$MaxMinutes = 8,
    [switch]$StrictExitCodes
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ZapRoot = Join-Path $RepoRoot "reports\security\zap"
$PostmanRoot = Join-Path $RepoRoot "tests\postman"
$ZapImage = "ghcr.io/zaproxy/zaproxy:stable"
$NewmanImage = "postman/newman:latest"

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

function Wait-ZapProxy {
    param([string]$Url)
    for ($i = 0; $i -lt 90; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "$Url/JSON/core/view/version/" -Method GET -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                return
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "ZAP proxy did not become ready in time"
}

function Save-ZapProxyReport {
    param(
        [string]$ProxyApi,
        [string]$ReportDir,
        [string]$Prefix
    )
    Invoke-WebRequest -Uri "$ProxyApi/OTHER/core/other/htmlreport/" -OutFile (Join-Path $ReportDir "$Prefix.html") -UseBasicParsing
    Invoke-WebRequest -Uri "$ProxyApi/OTHER/core/other/mdreport/" -OutFile (Join-Path $ReportDir "$Prefix.md") -UseBasicParsing
    Invoke-WebRequest -Uri "$ProxyApi/OTHER/core/other/jsonreport/" -OutFile (Join-Path $ReportDir "$Prefix.json") -UseBasicParsing
    Invoke-WebRequest -Uri "$ProxyApi/JSON/core/view/urls/" -OutFile (Join-Path $ReportDir "$Prefix.urls.json") -UseBasicParsing
}

function Invoke-NewmanThroughZap {
    $reportDir = New-ReportDir "newman"
    $prefix = "zap-newman-passive"
    $proxyPort = 8090
    $proxyApi = "http://localhost:$proxyPort"
    $postmanPath = (Resolve-Path $PostmanRoot).Path
    $containerName = "beauty_zap_passive_$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())"

    Write-Host "ZAP_MODE=newman"
    Write-Host "ZAP_PROXY_PORT=$proxyPort"
    Write-Host "ZAP_REPORT_DIR=$reportDir"

    & docker run -d --rm --name $containerName -p "${proxyPort}:8090" -v "${reportDir}:/zap/wrk/:rw" $ZapImage zap.sh -daemon -host 0.0.0.0 -port 8090 -config api.disablekey=true -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true | Out-Null
    try {
        Wait-ZapProxy -Url $proxyApi
        $newmanArgs = @(
            "run",
            "--rm",
            "-e",
            "HTTP_PROXY=http://host.docker.internal:${proxyPort}",
            "-e",
            "HTTPS_PROXY=http://host.docker.internal:${proxyPort}",
            "-v",
            "${postmanPath}:/etc/newman",
            $NewmanImage,
            "run",
            "/etc/newman/beauty_backend_acceptance.postman_collection.json",
            "-e",
            "/etc/newman/local-docker.postman_environment.json",
            "--env-var",
            "base_url=http://host.docker.internal:8000",
            "--bail",
            "--reporters",
            "cli,json",
            "--reporter-json-export",
            "/etc/newman/reports/newman-through-zap.json"
        )
        & docker @newmanArgs | ForEach-Object { Write-Host $_ }
        $newmanExit = $LASTEXITCODE
        Write-Host "NEWMAN_EXIT_CODE=$newmanExit"
        if ($newmanExit -ne 0) {
            throw "Newman-through-ZAP failed"
        }
        Start-Sleep -Seconds 5
        Save-ZapProxyReport -ProxyApi $proxyApi -ReportDir $reportDir -Prefix $prefix
        Assert-Artifacts -ReportDir $reportDir -Prefix $prefix
        & python (Join-Path $PSScriptRoot "zap_summarize_reports.py") --file (Join-Path $reportDir "$prefix.json") --urls-file (Join-Path $reportDir "$prefix.urls.json") | ForEach-Object { Write-Host $_ }
        return 0
    } finally {
        & docker stop $containerName 2>$null | Out-Null
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
