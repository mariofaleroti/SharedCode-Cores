param(
    [Parameter(Mandatory = $true)]
    [string]$InputJson,

    [string]$OutputDir = ".\output\manual_render",

    [string]$Formats = "html,txt,csv,xlsx",

    [switch]$Json,

    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $InputJson)) {
    throw "Input JSON not found: $InputJson"
}

Push-Location $ProjectRoot
try {
    $argsList = @(
        "-m", "render_core", "render",
        "--input", (Resolve-Path -LiteralPath $InputJson).Path,
        "--output-dir", $OutputDir,
        "--formats", $Formats
    )

    if ($Json) {
        $argsList += "--json"
    }

    python @argsList
}
finally {
    Pop-Location
}
