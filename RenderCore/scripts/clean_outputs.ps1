param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$targets = @(
    (Join-Path $ProjectRoot "output"),
    (Join-Path $ProjectRoot "dist"),
    (Join-Path $ProjectRoot "build"),
    (Join-Path $ProjectRoot ".tmp_smoke_json_contract_core")
)

foreach ($target in $targets) {
    if (Test-Path -LiteralPath $target) {
        Remove-Item -LiteralPath $target -Recurse -Force
        Write-Host "Removed: $target"
    }
}

Get-ChildItem -LiteralPath $ProjectRoot -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force

Write-Host "RenderCore local outputs cleaned."
