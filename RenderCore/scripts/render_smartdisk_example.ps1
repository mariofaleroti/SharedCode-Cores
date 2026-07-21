param(
    [Parameter(Mandatory = $true)]
    [string]$InputJson,

    [string]$OutputDir = ".\output\smartdisk_test",

    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "render_json.ps1") `
    -InputJson $InputJson `
    -OutputDir $OutputDir `
    -Formats "html,txt,csv,xlsx" `
    -Json `
    -ProjectRoot $ProjectRoot
