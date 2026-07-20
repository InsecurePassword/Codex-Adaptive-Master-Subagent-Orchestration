[CmdletBinding()]
param(
    [ValidateSet("auto", "minimal", "moderate", "heavy", "extreme")]
    [string]$Mode,
    [ValidateSet("user", "project")]
    [string]$Scope = "user",
    [string]$ProjectRoot = (Get-Location).Path,
    [switch]$Show,
    [switch]$DryRun
)
$ErrorActionPreference = "Stop"
$Python = Get-Command py -ErrorAction SilentlyContinue
if ($Python) { $Exe=$Python.Source; $Prefix=@("-3") }
else { $Python=Get-Command python -ErrorAction SilentlyContinue; if (-not $Python) { throw "Python 3.11+ was not found." }; $Exe=$Python.Source; $Prefix=@() }
$ArgsList=@($Prefix + @((Join-Path $PSScriptRoot "set_intensity.py"), "--scope", $Scope, "--project-root", $ProjectRoot))
if ($Mode) { $ArgsList += $Mode }
if ($Show) { $ArgsList += "--show" }
if ($DryRun) { $ArgsList += "--dry-run" }
& $Exe @ArgsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
