[CmdletBinding()]
param(
    [string]$HomeDirectory = $HOME,
    [switch]$SkipProfiles,
    [switch]$ExcludeSpark,
    [ValidateSet("low", "medium", "high")]
    [string[]]$SparkEfforts = @("low", "medium", "high"),
    [switch]$UpgradeManaged,
    [ValidateSet("auto", "minimal", "moderate", "heavy", "extreme")]
    [string]$Intensity = "auto",
    [switch]$WhatIf
)
$ErrorActionPreference = "Stop"
$Python = Get-Command py -ErrorAction SilentlyContinue
if ($Python) { $Exe=$Python.Source; $Prefix=@("-3") }
else { $Python=Get-Command python -ErrorAction SilentlyContinue; if (-not $Python) { throw "Python 3.11+ was not found." }; $Exe=$Python.Source; $Prefix=@() }
$ArgsList=@($Prefix + @((Join-Path $PSScriptRoot "scripts\install_package.py"), "--home", $HomeDirectory, "--spark-efforts", ($SparkEfforts -join ","), "--intensity", $Intensity))
if ($SkipProfiles) { $ArgsList += "--skip-profiles" }
if ($ExcludeSpark) { $ArgsList += "--exclude-spark" }
if ($UpgradeManaged) { $ArgsList += "--upgrade-managed" }
if ($WhatIf) { $ArgsList += "--dry-run" }
& $Exe @ArgsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
