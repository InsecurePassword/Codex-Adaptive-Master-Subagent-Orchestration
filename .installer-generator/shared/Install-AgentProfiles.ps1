[CmdletBinding()]
param(
    [string]$Destination,
    [switch]$ExcludeSpark,
    [ValidateSet("low", "medium", "high")]
    [string[]]$SparkEfforts = @("low", "medium", "high"),
    [switch]$UpgradeManaged,
    [switch]$DryRun,
    [switch]$Json,
    [string]$SolModel = "gpt-5.6",
    [string]$TerraModel = "gpt-5.6-terra",
    [string]$LunaModel = "gpt-5.6-luna",
    [string]$SparkModel = "gpt-5.3-codex-spark"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

function Resolve-Python311 {
    $Candidates = @()
    $Launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($Launcher) {
        $Candidates += [PSCustomObject]@{ Executable = $Launcher.Source; Prefix = @("-3") }
        foreach ($Version in @("3.14", "3.13", "3.12", "3.11")) {
            $Candidates += [PSCustomObject]@{ Executable = $Launcher.Source; Prefix = @("-$Version") }
        }
    }
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($Python) { $Candidates += [PSCustomObject]@{ Executable = $Python.Source; Prefix = @() } }
    $Python3 = Get-Command python3 -ErrorAction SilentlyContinue
    if ($Python3) { $Candidates += [PSCustomObject]@{ Executable = $Python3.Source; Prefix = @() } }

    foreach ($Candidate in $Candidates) {
        try {
            & $Candidate.Executable @($Candidate.Prefix + @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)")) 2>$null
            if ($LASTEXITCODE -eq 0) { return $Candidate }
        }
        catch { }
    }
    throw "Python 3.11 or later was not found."
}

$ResolvedPython = Resolve-Python311
$ScriptPath = Join-Path $PSScriptRoot "bootstrap_profiles.py"
if (-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
    throw "Profile installer was not found: $ScriptPath"
}
$Arguments = @($ResolvedPython.Prefix + @("-E", "-s", "-S") + @(
    $ScriptPath,
    "--sol-model", $SolModel,
    "--terra-model", $TerraModel,
    "--luna-model", $LunaModel,
    "--spark-model", $SparkModel
))
if ($Destination) { $Arguments += @("--destination", $Destination) }
if ($ExcludeSpark) { $Arguments += "--exclude-spark" }
else { $Arguments += @("--spark-efforts", ($SparkEfforts -join ",")) }
if ($UpgradeManaged) { $Arguments += "--upgrade-managed" }
if ($DryRun) { $Arguments += "--dry-run" }
if ($Json) { $Arguments += "--json" }

& $ResolvedPython.Executable @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "AMS profile installation failed with exit code $LASTEXITCODE."
}
