param(
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$SafeDirectory = $RepoRoot -replace "\\", "/"
$SafeGit = @("-c", "safe.directory=$SafeDirectory")

function Invoke-Git {
    param([string[]]$GitArgs)
    if ($VerboseOutput) {
        Write-Host "RUN git $(($SafeGit + $GitArgs) -join ' ')"
    }
    & git @SafeGit @GitArgs
    $exit = $LASTEXITCODE
    if ($exit -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $exit"
    }
}

function Test-Ignored {
    param([string]$Path)
    & git @SafeGit check-ignore -q $Path
    if ($LASTEXITCODE -ne 0) {
        throw "Generated artifact is not ignored: $Path"
    }
}

function Assert-NotTracked {
    param([string[]]$Paths)
    $tracked = & git @SafeGit ls-files @Paths
    if ($tracked) {
        Write-Host "TRACKED_FORBIDDEN_ARTIFACT_COUNT=$($tracked.Count)"
        foreach ($path in $tracked) {
            Write-Host "TRACKED_FORBIDDEN_ARTIFACT=$path"
        }
        throw "Forbidden local/generated artifacts are tracked."
    }
}

Set-Location $RepoRoot
Write-Host "GIT_HYGIENE_HOST=True"
Invoke-Git -GitArgs @("status", "--short")
Invoke-Git -GitArgs @("diff", "--check")
Assert-NotTracked -Paths @(
    ".env",
    "db.sqlite3",
    "tests/postman/reports/newman-local.json",
    "tests/postman/reports/newman-through-zap.json",
    "reports/security/zap/health/zap-health-baseline.html",
    "reports/security/zap/health/zap-health-baseline.json",
    "reports/security/zap/root/zap-root-baseline.html",
    "reports/security/zap/root/zap-root-baseline.json",
    "reports/security/zap/api/zap-api-baseline.html",
    "reports/security/zap/api/zap-api-baseline.json",
    "reports/security/zap/newman/zap-newman-passive.html",
    "reports/security/zap/newman/zap-newman-passive.json"
)

$ignoredArtifacts = @(
    "tests/postman/reports/newman-local.json",
    "tests/postman/reports/newman-through-zap.json",
    "reports/security/zap/health/zap-health-baseline.html",
    "reports/security/zap/root/zap-root-baseline.html",
    "reports/security/zap/api/zap-api-baseline.html",
    "reports/security/zap/newman/zap-newman-passive.html",
    "reports/ci/turbo-pass-summary.md"
)
foreach ($artifact in $ignoredArtifacts) {
    Test-Ignored -Path $artifact
}

$secretPatterns = @(
    "(?i)(DARAJA_CONSUMER_SECRET|DARAJA_PASSKEY|EMAIL_HOST_PASSWORD|AWS_SECRET_ACCESS_KEY|R2_SECRET_ACCESS_KEY)\s*=\s*['""]?(?!\$|replace-|$)([A-Za-z0-9_./+=:-]{16,})",
    "(?i)SECRET_KEY\s*=\s*['""]?(?!\$|replace-|django-insecure|phase1-phase2|production-secure-smoke-test|$)(.{24,})",
    "(?i)(sk_live_|sk_test_|pk_live_|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{20,})",
    "(?i)DEBUG\s*=\s*True"
)

$trackedFiles = & git @SafeGit ls-files
$hits = New-Object System.Collections.Generic.List[string]
foreach ($file in $trackedFiles) {
    if ($file -match "^(reports/security/zap|tests/postman/reports)/") {
        continue
    }
    if ($file -match "^(docs/|tests/)|/tests/|\.example$|^scripts/ci/django_smoke\.sh$") {
        continue
    }
    if (!(Test-Path $file -PathType Leaf)) {
        continue
    }
    $lines = Get-Content -Path $file -ErrorAction SilentlyContinue
    foreach ($line in $lines) {
        if ($line -match "os\.environ|getenv|process\.env|\$\{") {
            continue
        }
        foreach ($pattern in $secretPatterns) {
            if ($line -match $pattern) {
                $hits.Add($file)
                break
            }
        }
        if ($hits.Contains($file)) {
            break
        }
    }
}

$uniqueHits = $hits | Sort-Object -Unique
Write-Host "GIT_SECRET_MARKER_FILE_COUNT=$($uniqueHits.Count)"
foreach ($file in $uniqueHits) {
    Write-Host "GIT_SECRET_MARKER_FILE=$file"
}
if ($uniqueHits.Count -gt 0) {
    throw "Host git hygiene found high-confidence secret/debug markers in tracked files."
}
Write-Host "GIT_HYGIENE_RESULT=passed"
