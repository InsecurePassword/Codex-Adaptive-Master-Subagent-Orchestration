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
    [switch]$Uninstall,
    [switch]$Force,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

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
$Installer = Join-Path $PSScriptRoot "scripts\install_package.py"
if (-not (Test-Path -LiteralPath $Installer -PathType Leaf)) {
    throw "Package installer was not found: $Installer"
}

$Arguments = @($ResolvedPython.Prefix + @("-B", "-E", "-s", "-S", $Installer, "--home", $HomeDirectory))
if ($Uninstall) {
    $Arguments += "--uninstall"
    if ($WhatIf) { $Arguments += "--dry-run" }
    elseif ($Force) { $Arguments += "--yes" }
    else {
        $Confirmation = Read-Host "Type REMOVE to uninstall all package-managed AMS files"
        if ($Confirmation -cne "REMOVE") {
            Write-Host "Uninstall cancelled."
            return
        }
        $Arguments += "--yes"
    }
}
else {
    $Arguments += @("--spark-efforts", ($SparkEfforts -join ","), "--intensity", $Intensity)
    if ($SkipProfiles) { $Arguments += "--skip-profiles" }
    if ($ExcludeSpark) { $Arguments += "--exclude-spark" }
    if ($UpgradeManaged) { $Arguments += "--upgrade-managed" }
    if ($WhatIf) { $Arguments += "--dry-run" }
}

& $ResolvedPython.Executable @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "AMS package operation failed with exit code $LASTEXITCODE."
}
