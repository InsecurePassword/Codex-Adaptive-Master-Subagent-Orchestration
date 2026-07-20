[CmdletBinding()]
param(
    [string]$Destination,
    [switch]$ExcludeSpark,
    [object]$SparkEfforts = "low,medium,high",
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

function ConvertTo-SparkEffortList {
    param([AllowNull()][object]$Value)

    $Values = @()
    foreach ($Entry in @($Value)) {
        if ($null -eq $Entry) { continue }
        foreach ($Part in ([string]$Entry).Split(",")) {
            $Normalized = $Part.Trim().ToLowerInvariant()
            if ([string]::IsNullOrWhiteSpace($Normalized)) { continue }
            if (@("low", "medium", "high") -notcontains $Normalized) {
                throw "Unsupported Spark effort value: $Part"
            }
            if ($Values -notcontains $Normalized) {
                $Values += $Normalized
            }
        }
    }
    return $Values
}

function Resolve-Python311 {
    $Candidates = @()
    $Launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($Launcher) {
        foreach ($Prefix in @(@("-3"), @("-3.14"), @("-3.13"), @("-3.12"), @("-3.11"))) {
            $Candidates += [PSCustomObject]@{ Executable = $Launcher.Source; Prefix = $Prefix }
        }
    }
    foreach ($Name in @("python", "python3")) {
        $Command = Get-Command $Name -ErrorAction SilentlyContinue
        if ($Command) { $Candidates += [PSCustomObject]@{ Executable = $Command.Source; Prefix = @() } }
    }
    foreach ($Candidate in $Candidates) {
        try {
            & $Candidate.Executable @($Candidate.Prefix + @("-B", "-E", "-s", "-S", "-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)")) 2>$null
            if ($LASTEXITCODE -eq 0) { return $Candidate }
        }
        catch { }
    }
    throw "Python 3.11 or later was not found."
}

$ResolvedPython = Resolve-Python311
$SparkEffortValues = @(ConvertTo-SparkEffortList -Value $SparkEfforts)
if (-not $ExcludeSpark -and $SparkEffortValues.Count -eq 0) { throw "SparkEfforts cannot be empty unless Spark is excluded." }
$ScriptPath = Join-Path $PSScriptRoot "bootstrap_profiles.py"
if (-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
    throw "Profile installer was not found: $ScriptPath"
}
$Arguments = @($ResolvedPython.Prefix + @(
    "-B", "-E", "-s", "-S", $ScriptPath,
    "--sol-model", $SolModel,
    "--terra-model", $TerraModel,
    "--luna-model", $LunaModel,
    "--spark-model", $SparkModel
))
if ($Destination) { $Arguments += @("--destination", $Destination) }
if ($ExcludeSpark) { $Arguments += "--exclude-spark" }
else { $Arguments += @("--spark-efforts", ($SparkEffortValues -join ",")) }
if ($UpgradeManaged) { $Arguments += "--upgrade-managed" }
if ($DryRun) { $Arguments += "--dry-run" }
if ($Json) { $Arguments += "--json" }

& $ResolvedPython.Executable @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "AMS profile installation failed with exit code $LASTEXITCODE."
}
