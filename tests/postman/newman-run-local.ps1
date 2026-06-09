$ErrorActionPreference = "Stop"
$reports = Join-Path $PSScriptRoot "reports"
New-Item -ItemType Directory -Force $reports | Out-Null
newman.cmd run `
  (Join-Path $PSScriptRoot "beauty_backend_acceptance.postman_collection.json") `
  -e (Join-Path $PSScriptRoot "local-docker.postman_environment.json") `
  --bail `
  --reporters cli,json `
  --reporter-json-export (Join-Path $reports "newman-local.json")
