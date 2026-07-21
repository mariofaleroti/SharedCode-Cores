param(
    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location $ProjectRoot
try {
    python -m pip install -r requirements.txt
    pyinstaller apps/render_engine/RenderEngine.spec --clean --noconfirm

    $releaseRoot = Join-Path $ProjectRoot "release\RenderEngine"
    if (Test-Path $releaseRoot) {
        Remove-Item $releaseRoot -Recurse -Force
    }

    New-Item -ItemType Directory -Path (Split-Path $releaseRoot -Parent) -Force | Out-Null
    Copy-Item -Path (Join-Path $ProjectRoot "dist\RenderEngine") -Destination $releaseRoot -Recurse -Force
    Copy-Item -Path (Join-Path $ProjectRoot "apps\render_engine\tool_manifest.json") -Destination (Join-Path $releaseRoot "tool_manifest.json") -Force

    Write-Host "Release generado en: $releaseRoot"
}
finally {
    Pop-Location
}
