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

if ($Show -and $Mode) { throw "-Show and -Mode cannot be used together." }
if ($DryRun -and -not $Mode) { throw "-DryRun requires -Mode." }

$ResolvedPython = Resolve-Python311
$ScriptPath = Join-Path $PSScriptRoot "set_intensity.py"
if (-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
    throw "Intensity utility was not found: $ScriptPath"
}
$Arguments = @($ResolvedPython.Prefix + @("-B", "-E", "-s", "-S", $ScriptPath, "--scope", $Scope, "--project-root", $ProjectRoot))
if ($Mode) { $Arguments += $Mode }
if ($Show) { $Arguments += "--show" }
if ($DryRun) { $Arguments += "--dry-run" }

& $ResolvedPython.Executable @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "AMS intensity operation failed with exit code $LASTEXITCODE."
}
