# Adaptive Master-Subagent Orchestration installer
# Version 3.1.0

[CmdletBinding()]
param(
    [Alias("InstallOption")]
    [ValidateSet("A", "B", "C", "Uninstall", "Remove", "1", "2", "3", "4")]
    [string]$Option,

    [string]$HomeDirectory = $HOME,

    [ValidateSet("auto", "minimal", "moderate", "heavy", "extreme")]
    [string]$Intensity = "auto",

    [ValidateSet("low", "medium", "high")]
    [string[]]$SparkEfforts = @("low", "medium", "high"),

    [switch]$ExcludeSpark,
    [switch]$Force,
    [string]$ArchivePath,
    [Alias("Ref")]
    [string]$RepositoryRef
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

$Repository = "InsecurePassword/adaptive-master-subagent-orchestration"
$Ref = if (-not [string]::IsNullOrWhiteSpace($RepositoryRef)) { $RepositoryRef.Trim() } elseif ([string]::IsNullOrWhiteSpace($env:AMS_REF)) { "main" } else { $env:AMS_REF.Trim() }
$ArchiveName = "adaptive-master-subagent-orchestration-$($Ref.Replace('/', '-')).zip"
$ArchiveUrl = "https://github.com/$Repository/archive/refs/heads/$Ref.zip"
$ApiArchiveUrl = "https://api.github.com/repos/$Repository/zipball/$Ref"
$ConnectTimeoutSeconds = 15
$DownloadTimeoutSeconds = 120

function Write-Heading {
    param([Parameter(Mandatory = $true)][string]$Text)
    Write-Host ""
    Write-Host $Text -ForegroundColor Cyan
    Write-Host ("=" * $Text.Length) -ForegroundColor DarkCyan
}

function Get-PositiveEnvironmentInteger {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][int]$Default
    )
    $Value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $Default }
    $Parsed = 0
    if (-not [int]::TryParse($Value, [ref]$Parsed) -or $Parsed -le 0) {
        throw "$Name must be a positive integer; received: $Value"
    }
    return $Parsed
}

function Get-NormalizedOption {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $null }
    switch ($Value.Trim().ToUpperInvariant()) {
        "1" { return "A" }
        "A" { return "A" }
        "2" { return "B" }
        "B" { return "B" }
        "3" { return "C" }
        "C" { return "C" }
        "4" { return "UNINSTALL" }
        "UNINSTALL" { return "UNINSTALL" }
        "REMOVE" { return "UNINSTALL" }
        default { throw "Unsupported selection: $Value" }
    }
}

function Get-UserSelection {
    Write-Heading "Adaptive Master-Subagent Orchestration"
    Write-Host "Choose one installation option:"
    Write-Host ""
    Write-Host "  1) Option A - Installer skill + permanent runtime (Recommended)" -ForegroundColor Green
    Write-Host "  2) Option B - Unified skill with conditional bootstrap"
    Write-Host "  3) Option C - Lean runtime with mandatory deterministic installation"
    Write-Host "  4) Uninstall Adaptive Master-Subagent Orchestration"
    Write-Host ""
    $Choice = Read-Host "Selection [1]"
    if ([string]::IsNullOrWhiteSpace($Choice)) { $Choice = "1" }
    return Get-NormalizedOption $Choice
}

function Confirm-Uninstall {
    if ($Force -or $env:AMS_UNINSTALL_FORCE -eq "1") { return $true }
    Write-Warning "This removes package-managed AMS plugins, profiles, backups, legacy skill directories, and the user-level AMS configuration."
    Write-Host "Unrelated files and project-local configuration are preserved."
    $Confirmation = Read-Host "Type REMOVE to continue"
    return ($Confirmation -ceq "REMOVE")
}

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

function Invoke-ResolvedPython {
    param(
        [Parameter(Mandatory = $true)]$Python,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )
    & $Python.Executable @($Python.Prefix + @("-B", "-E", "-s", "-S") + $Arguments)
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE."
    }
}

function Copy-Or-DownloadArchive {
    param(
        [Parameter(Mandatory = $true)][string]$Destination,
        [string]$RequestedArchivePath
    )
    if ([string]::IsNullOrWhiteSpace($RequestedArchivePath)) { $RequestedArchivePath = $env:AMS_ARCHIVE_PATH }
    if (-not [string]::IsNullOrWhiteSpace($RequestedArchivePath)) {
        $Resolved = [System.IO.Path]::GetFullPath($RequestedArchivePath)
        if (-not (Test-Path -LiteralPath $Resolved -PathType Leaf)) {
            throw "Archive path is not a readable file: $RequestedArchivePath"
        }
        Copy-Item -LiteralPath $Resolved -Destination $Destination -Force
        Write-Host "Using repository archive: $Resolved"
        return
    }

    $Headers = @{}
    $Url = $ArchiveUrl
    if (-not [string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)) {
        $Url = $ApiArchiveUrl
        $Headers["Authorization"] = "Bearer $($env:GITHUB_TOKEN)"
        $Headers["Accept"] = "application/vnd.github+json"
        $Headers["X-GitHub-Api-Version"] = "2022-11-28"
    }
    Write-Host "Downloading repository package for ref $Ref."
    $Curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    try {
        if ($Curl) {
            $CurlArguments = @(
                "-fL", "--silent", "--show-error", "--retry", "3", "--retry-delay", "1",
                "--connect-timeout", [string]$ConnectTimeoutSeconds, "--max-time", [string]$DownloadTimeoutSeconds
            )
            foreach ($Key in $Headers.Keys) {
                $CurlArguments += @("-H", "$Key`: $($Headers[$Key])")
            }
            $CurlArguments += @($Url, "-o", $Destination)
            & $Curl.Source @CurlArguments
            if ($LASTEXITCODE -ne 0) { throw "curl.exe exited with code $LASTEXITCODE" }
        }
        else {
            $Request = @{
                Uri = $Url
                OutFile = $Destination
                UseBasicParsing = $true
                TimeoutSec = $DownloadTimeoutSeconds
                ErrorAction = "Stop"
            }
            if ($Headers.Count -gt 0) { $Request["Headers"] = $Headers }
            Invoke-WebRequest @Request
        }
    }
    catch {
        throw "Repository package download failed. Verify connectivity and repository access. $($_.Exception.Message)"
    }
    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf) -or (Get-Item -LiteralPath $Destination).Length -le 0) {
        throw "Repository package download produced an empty file."
    }
}

function Expand-SafeArchive {
    param(
        [Parameter(Mandatory = $true)]$Python,
        [Parameter(Mandatory = $true)][string]$Archive,
        [Parameter(Mandatory = $true)][string]$Destination,
        [Parameter(Mandatory = $true)][string]$TempRoot
    )
    $ExtractorPath = Join-Path $TempRoot "safe_extract.py"
    $Extractor = @'
from __future__ import annotations
import os
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

archive = Path(sys.argv[1])
destination = Path(sys.argv[2])
max_entries = 5000
max_bytes = 256 * 1024 * 1024
seen = set()
try:
    with zipfile.ZipFile(archive) as zf:
        infos = zf.infolist()
        if not infos:
            raise SystemExit("Repository archive is empty.")
        if len(infos) > max_entries:
            raise SystemExit(f"Repository archive has too many entries: {len(infos)}")
        total = 0
        validated = []
        for info in infos:
            name = info.filename.replace("\\", "/")
            if any(ord(char) < 32 or ord(char) == 127 for char in name):
                raise SystemExit(f"Repository archive contains a control character in a path: {name!r}")
            path = PurePosixPath(name)
            if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
                raise SystemExit(f"Repository archive contains an unsafe path: {name}")
            if path.parts and ":" in path.parts[0]:
                raise SystemExit(f"Repository archive contains an unsupported drive path: {name}")
            normalized = path.as_posix().rstrip("/")
            if normalized in seen:
                raise SystemExit(f"Repository archive contains a duplicate path: {name}")
            seen.add(normalized)
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise SystemExit(f"Repository archive contains an unsupported symbolic link: {name}")
            if info.flag_bits & 0x1:
                raise SystemExit(f"Repository archive contains an encrypted entry: {name}")
            total += info.file_size
            if total > max_bytes:
                raise SystemExit("Repository archive exceeds the extraction size limit.")
            validated.append((info, path))
        destination.mkdir(parents=True, exist_ok=True)
        root = destination.resolve()
        for info, path in validated:
            target = destination.joinpath(*path.parts)
            resolved_parent = target.parent.resolve(strict=False)
            if os.path.commonpath((str(root), str(resolved_parent))) != str(root):
                raise SystemExit(f"Repository archive escapes the extraction directory: {info.filename}")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as source, target.open("wb") as output:
                while True:
                    block = source.read(1024 * 1024)
                    if not block:
                        break
                    output.write(block)
except (OSError, zipfile.BadZipFile) as exc:
    raise SystemExit(f"Repository archive could not be extracted: {exc}") from exc
'@
    $Utf8NoBom = New-Object System.Text.UTF8Encoding -ArgumentList $false
    [System.IO.File]::WriteAllText($ExtractorPath, $Extractor, $Utf8NoBom)
    Invoke-ResolvedPython -Python $Python -Arguments @($ExtractorPath, $Archive, $Destination)
}

function Get-PackageRoot {
    param(
        [Parameter(Mandatory = $true)][string]$ExtractPath,
        [Parameter(Mandatory = $true)][string]$DirectoryName
    )
    $Matches = @(Get-ChildItem -LiteralPath $ExtractPath -Directory -Recurse -ErrorAction Stop | Where-Object { $_.Name -ceq $DirectoryName })
    if ($Matches.Count -ne 1) {
        throw "Expected exactly one package directory named $DirectoryName after extraction; found $($Matches.Count)."
    }
    return $Matches[0].FullName
}

function Get-InstalledUninstaller {
    param([Parameter(Mandatory = $true)]$Python)
    $Finder = @'
from pathlib import Path
import sys
names = (
    "adaptive-master-subagent-orchestration-option-a-two-skill",
    "adaptive-master-subagent-orchestration-option-b-unified",
    "adaptive-master-subagent-orchestration-option-c-installer-required",
    "adaptive-master-subagent-orchestration-option-a-modular",
    "adaptive-master-subagent-orchestration-option-c-lean",
    "adaptive-master-subagent-orchestration",
)
home = Path(sys.argv[1]).expanduser().resolve(strict=False)
plugin_root = home / ".agents" / "plugins" / "plugins"
for name in names:
    candidate = plugin_root / name / "scripts" / "install_package.py"
    if candidate.is_file() and not candidate.is_symlink():
        print(candidate)
        raise SystemExit(0)
backup_root = home / ".agents" / "plugins" / "backups"
for name in names:
    for backup in sorted(backup_root.glob(f"{name}.backup-*"), reverse=True):
        candidate = backup / "scripts" / "install_package.py"
        if candidate.is_file() and not candidate.is_symlink():
            print(candidate)
            raise SystemExit(0)
raise SystemExit(3)
'@
    $FinderPath = Join-Path ([System.IO.Path]::GetTempPath()) ("ams-find-uninstaller-" + [Guid]::NewGuid().ToString("N") + ".py")
    $Utf8NoBom = New-Object System.Text.UTF8Encoding -ArgumentList $false
    [System.IO.File]::WriteAllText($FinderPath, $Finder, $Utf8NoBom)
    try {
        $Output = & $Python.Executable @($Python.Prefix + @("-B", "-E", "-s", "-S", $FinderPath, $HomeDirectory))
        $Code = $LASTEXITCODE
    }
    finally {
        Remove-Item -LiteralPath $FinderPath -Force -ErrorAction SilentlyContinue
    }
    if ($Code -eq 0) {
        $Candidate = [string]($Output | Select-Object -Last 1)
        if ([string]::IsNullOrWhiteSpace($Candidate)) {
            throw "Installed AMS uninstaller discovery returned an empty path."
        }
        return $Candidate.Trim()
    }
    if ($Code -eq 3) { return $null }
    throw "Installed AMS uninstaller discovery failed with exit code $Code."
}

try {
    $ConnectTimeoutSeconds = Get-PositiveEnvironmentInteger -Name "AMS_CONNECT_TIMEOUT_SECONDS" -Default 15
    $DownloadTimeoutSeconds = Get-PositiveEnvironmentInteger -Name "AMS_DOWNLOAD_TIMEOUT_SECONDS" -Default 120

    if ([string]::IsNullOrWhiteSpace($Ref) -or $Ref.StartsWith("/") -or $Ref.Contains("..") -or $Ref -notmatch '^[A-Za-z0-9._/-]+$') {
        throw "Unsupported repository ref: $Ref"
    }
    if (-not $PSBoundParameters.ContainsKey("HomeDirectory") -and -not [string]::IsNullOrWhiteSpace($env:AMS_HOME)) {
        $HomeDirectory = $env:AMS_HOME
    }
    if ([string]::IsNullOrWhiteSpace($HomeDirectory)) { throw "HomeDirectory cannot be empty." }
    $HomeDirectory = [System.IO.Path]::GetFullPath($HomeDirectory)

    if ([string]::IsNullOrWhiteSpace($Option) -and -not [string]::IsNullOrWhiteSpace($env:AMS_INSTALL_OPTION)) {
        $Option = $env:AMS_INSTALL_OPTION
    }
    if (-not [string]::IsNullOrWhiteSpace($env:AMS_INTENSITY)) {
        $EnvironmentIntensity = $env:AMS_INTENSITY.Trim().ToLowerInvariant()
        if (@("auto", "minimal", "moderate", "heavy", "extreme") -notcontains $EnvironmentIntensity) {
            throw "Unsupported AMS_INTENSITY value: $($env:AMS_INTENSITY)"
        }
        $Intensity = $EnvironmentIntensity
    }
    if (-not [string]::IsNullOrWhiteSpace($env:AMS_SPARK_EFFORTS)) {
        $EnvironmentSparkEfforts = @($env:AMS_SPARK_EFFORTS.Split(",") | ForEach-Object { $_.Trim().ToLowerInvariant() } | Where-Object { $_ })
        foreach ($Effort in $EnvironmentSparkEfforts) {
            if (@("low", "medium", "high") -notcontains $Effort) {
                throw "Unsupported AMS_SPARK_EFFORTS value: $Effort"
            }
        }
        $SparkEfforts = $EnvironmentSparkEfforts
    }
    if ($env:AMS_EXCLUDE_SPARK -notin @($null, "", "0", "1")) {
        throw "AMS_EXCLUDE_SPARK must be 0 or 1; received: $($env:AMS_EXCLUDE_SPARK)"
    }
    if ($env:AMS_UNINSTALL_FORCE -notin @($null, "", "0", "1")) {
        throw "AMS_UNINSTALL_FORCE must be 0 or 1; received: $($env:AMS_UNINSTALL_FORCE)"
    }
    if (-not ($ExcludeSpark -or $env:AMS_EXCLUDE_SPARK -eq "1") -and $SparkEfforts.Count -eq 0) {
        throw "SparkEfforts cannot be empty unless Spark is excluded."
    }

    $Selected = Get-NormalizedOption $Option
    if ($null -eq $Selected) { $Selected = Get-UserSelection }
    if ($Selected -eq "UNINSTALL" -and -not (Confirm-Uninstall)) {
        Write-Host "Uninstall cancelled."
        exit 0
    }

    $Python = Resolve-Python311
    if ($Selected -eq "UNINSTALL") {
        $InstalledUninstaller = Get-InstalledUninstaller -Python $Python
        if (-not [string]::IsNullOrWhiteSpace($InstalledUninstaller)) {
            Write-Heading "Uninstalling Adaptive Master-Subagent Orchestration"
            Invoke-ResolvedPython -Python $Python -Arguments @($InstalledUninstaller, "--home", $HomeDirectory, "--uninstall", "--yes")
            Write-Host ""
            Write-Host "Uninstall completed successfully. Restart Codex to refresh discovered plugins and agents." -ForegroundColor Green
            exit 0
        }
        Write-Host "No package-managed AMS installation was found."
        exit 0
    }
    $TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("ams-install-" + [Guid]::NewGuid().ToString("N"))
    $ArchiveFile = Join-Path $TempRoot $ArchiveName
    $ExtractPath = Join-Path $TempRoot "extracted"
    New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null
    try {
        Copy-Or-DownloadArchive -Destination $ArchiveFile -RequestedArchivePath $ArchivePath
        Expand-SafeArchive -Python $Python -Archive $ArchiveFile -Destination $ExtractPath -TempRoot $TempRoot

        $OptionDirectories = @{
            "A" = "adaptive-master-subagent-orchestration-option-a-two-skill"
            "B" = "adaptive-master-subagent-orchestration-option-b-unified"
            "C" = "adaptive-master-subagent-orchestration-option-c-installer-required"
            "UNINSTALL" = "adaptive-master-subagent-orchestration-option-c-installer-required"
        }
        $PackageRoot = Get-PackageRoot -ExtractPath $ExtractPath -DirectoryName $OptionDirectories[$Selected]
        $Installer = Join-Path $PackageRoot "scripts\install_package.py"
        if (-not (Test-Path -LiteralPath $Installer -PathType Leaf)) {
            throw "Selected package installer was not found: $Installer"
        }

        if ($Selected -eq "UNINSTALL") {
            Write-Heading "Uninstalling Adaptive Master-Subagent Orchestration"
            Invoke-ResolvedPython -Python $Python -Arguments @($Installer, "--home", $HomeDirectory, "--uninstall", "--yes")
            Write-Host ""
            Write-Host "Uninstall completed successfully. Restart Codex to refresh discovered plugins and agents." -ForegroundColor Green
        }
        else {
            Write-Heading "Installing Option $Selected"
            $Arguments = @($Installer, "--home", $HomeDirectory, "--upgrade-managed", "--intensity", $Intensity, "--spark-efforts", ($SparkEfforts -join ","))
            if ($ExcludeSpark -or $env:AMS_EXCLUDE_SPARK -eq "1") { $Arguments += "--exclude-spark" }
            Invoke-ResolvedPython -Python $Python -Arguments $Arguments
            Write-Host ""
            Write-Host "Option $Selected installed successfully. Restart Codex if it does not appear immediately." -ForegroundColor Green
        }
    }
    finally {
        if (Test-Path -LiteralPath $TempRoot) {
            Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
