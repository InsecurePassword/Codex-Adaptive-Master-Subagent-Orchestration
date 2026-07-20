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
$ScriptPath = Join-Path $PSScriptRoot "bootstrap_profiles.py"
$Python = Get-Command py -ErrorAction SilentlyContinue
$Prefix = @()
if ($Python) {
    $Executable = $Python.Source
    $Prefix = @("-3")
} else {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Python) { throw "Python 3.11+ was not found (tried 'py' and 'python')." }
    $Executable = $Python.Source
}

$Arguments = @($Prefix + @(
    $ScriptPath,
    "--sol-model", $SolModel,
    "--terra-model", $TerraModel,
    "--luna-model", $LunaModel,
    "--spark-model", $SparkModel
))
if ($Destination) { $Arguments += @("--destination", $Destination) }
if ($ExcludeSpark) {
    $Arguments += "--exclude-spark"
} else {
    $Arguments += @("--spark-efforts", ($SparkEfforts -join ","))
}
if ($UpgradeManaged) { $Arguments += "--upgrade-managed" }
if ($DryRun) { $Arguments += "--dry-run" }
if ($Json) { $Arguments += "--json" }

& $Executable @Arguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
