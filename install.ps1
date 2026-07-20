# Adaptive Master-Subagent Orchestration remote installer
# Version 3.1.0

[CmdletBinding()]
param(
    [ValidateSet("A", "B", "C", "Uninstall", "1", "2", "3", "4")]
    [string]$Option,

    [ValidateSet("auto", "minimal", "moderate", "heavy", "extreme")]
    [string]$Intensity = "auto",

    [ValidateSet("low", "medium", "high")]
    [string[]]$SparkEfforts = @("low", "medium", "high"),

    [switch]$ExcludeSpark,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

$Repository = "InsecurePassword/adaptive-master-subagent-orchestration"
$Ref = "main"
$ReleaseVersion = "3.1.0"
$ArchiveName = "adaptive-master-subagent-orchestration-$Ref.zip"
$ManagedMarker = "# managed-by: adaptive-master-subagent-orchestration"
$PublicArchiveUrl = "https://github.com/$Repository/archive/refs/heads/$Ref.zip"
$PrivateArchiveUrl = "https://api.github.com/repos/$Repository/zipball/$Ref"

$PluginNames = @(
    "adaptive-master-subagent-orchestration-option-a-two-skill",
    "adaptive-master-subagent-orchestration-option-b-unified",
    "adaptive-master-subagent-orchestration-option-c-installer-required",
    "adaptive-master-subagent-orchestration-option-a-modular",
    "adaptive-master-subagent-orchestration-option-c-lean",
    "adaptive-master-subagent-orchestration"
)

function Write-Heading {
    param([string]$Text)
    Write-Host ""
    Write-Host $Text -ForegroundColor Cyan
    Write-Host ("=" * $Text.Length) -ForegroundColor DarkCyan
}

function Get-NormalizedOption {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $null
    }

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

    $choice = Read-Host "Selection [1]"
    if ([string]::IsNullOrWhiteSpace($choice)) {
        $choice = "1"
    }
    return Get-NormalizedOption $choice
}

function Get-CodexHome {
    if (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
        return [System.IO.Path]::GetFullPath($env:CODEX_HOME)
    }
    return (Join-Path $HOME ".codex")
}

function Confirm-Uninstall {
    if ($Force -or $env:AMS_UNINSTALL_FORCE -eq "1") {
        return $true
    }

    Write-Warning "This removes package-managed plugins, managed agent profiles, legacy skill directories, and the user-level AMS configuration."
    Write-Host "Project-local .codex configuration files and unrelated user files will not be removed."
    $confirmation = Read-Host "Type REMOVE to continue"
    return ($confirmation -ceq "REMOVE")
}

function Remove-AmsInstallation {
    Write-Heading "Uninstalling Adaptive Master-Subagent Orchestration"

    if (-not (Confirm-Uninstall)) {
        Write-Host "Uninstall cancelled."
        return
    }

    $marketRoot = Join-Path $HOME ".agents\plugins"
    $pluginRoot = Join-Path $marketRoot "plugins"
    $marketplacePath = Join-Path $marketRoot "marketplace.json"
    $codexHome = Get-CodexHome
    $agentsPath = Join-Path $codexHome "agents"
    $configPath = Join-Path $codexHome "ams-orchestration.toml"

    if (Test-Path -LiteralPath $pluginRoot) {
        Get-ChildItem -LiteralPath $pluginRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $directoryName = $_.Name
            $owned = $false
            foreach ($pluginName in $PluginNames) {
                if ($directoryName -eq $pluginName -or
                    $directoryName.StartsWith("$pluginName.backup-", [System.StringComparison]::OrdinalIgnoreCase) -or
                    $directoryName.StartsWith("$pluginName.installing-", [System.StringComparison]::OrdinalIgnoreCase)) {
                    $owned = $true
                    break
                }
            }
            if ($owned) {
                Remove-Item -LiteralPath $_.FullName -Recurse -Force
                Write-Host "removed plugin directory: $($_.FullName)"
            }
        }
    }

    if (Test-Path -LiteralPath $marketplacePath) {
        try {
            $marketplace = Get-Content -LiteralPath $marketplacePath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($null -ne $marketplace.plugins) {
                $remaining = @($marketplace.plugins | Where-Object { $PluginNames -notcontains $_.name })
                $marketplace.plugins = $remaining
                $json = $marketplace | ConvertTo-Json -Depth 100
                $utf8NoBom = New-Object System.Text.UTF8Encoding -ArgumentList $false
                [System.IO.File]::WriteAllText($marketplacePath, $json + [Environment]::NewLine, $utf8NoBom)
                Write-Host "updated marketplace registration: $marketplacePath"
            }
        }
        catch {
            throw "Unable to safely update $marketplacePath. No marketplace entries were intentionally removed. $($_.Exception.Message)"
        }
    }

    if (Test-Path -LiteralPath $agentsPath) {
        Get-ChildItem -LiteralPath $agentsPath -File -ErrorAction SilentlyContinue | ForEach-Object {
            try {
                $content = Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 -ErrorAction Stop
                if ($content.Contains($ManagedMarker)) {
                    Remove-Item -LiteralPath $_.FullName -Force
                    Write-Host "removed managed profile: $($_.FullName)"
                }
            }
            catch {
                Write-Warning "Could not inspect $($_.FullName): $($_.Exception.Message)"
            }
        }
    }

    if (Test-Path -LiteralPath $configPath) {
        Remove-Item -LiteralPath $configPath -Force
        Write-Host "removed user configuration: $configPath"
    }

    $legacySkillRoot = Join-Path $HOME ".agents\skills"
    foreach ($legacySkillName in @("adaptive-master-subagent-orchestration", "ams-orchestration", "ams-installer")) {
        $legacySkillPath = Join-Path $legacySkillRoot $legacySkillName
        if (Test-Path -LiteralPath $legacySkillPath) {
            Remove-Item -LiteralPath $legacySkillPath -Recurse -Force
            Write-Host "removed legacy skill directory: $legacySkillPath"
        }
    }

    Write-Host ""
    Write-Host "Uninstall complete. Restart Codex to refresh discovered plugins and agents." -ForegroundColor Green
}

function Assert-Python311 {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        & $launcher.Source -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
        if ($LASTEXITCODE -eq 0) {
            return
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        & $python.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
        if ($LASTEXITCODE -eq 0) {
            return
        }
    }

    throw "Python 3.11 or later is required. Install Python, then run this installer again."
}

function Download-ReleaseArchive {
    param([string]$Destination)

    $headers = @{}
    $archiveUrl = $PublicArchiveUrl
    if (-not [string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)) {
        $archiveUrl = $PrivateArchiveUrl
        $headers["Authorization"] = "Bearer $($env:GITHUB_TOKEN)"
        $headers["Accept"] = "application/vnd.github+json"
        $headers["X-GitHub-Api-Version"] = "2022-11-28"
    }

    Write-Host "Downloading repository package: $archiveUrl"
    $request = @{
        Uri = $archiveUrl
        OutFile = $Destination
        UseBasicParsing = $true
        ErrorAction = "Stop"
    }
    if ($headers.Count -gt 0) {
        $request["Headers"] = $headers
    }

    try {
        Invoke-WebRequest @request
    }
    catch {
        $privateHint = ""
        if ([string]::IsNullOrWhiteSpace($env:GITHUB_TOKEN)) {
            $privateHint = " The repository is private; set GITHUB_TOKEN to a token with repository read access and retry."
        }
        throw "Repository package download failed.$privateHint $($_.Exception.Message)"
    }
}

function Test-PackageManifest {
    param([string]$PackageRoot)

    $manifestPath = Join-Path $PackageRoot "MANIFEST.sha256"
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw "Package manifest was not found: $manifestPath"
    }

    foreach ($line in Get-Content -LiteralPath $manifestPath -Encoding UTF8) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        if ($line -notmatch '^([0-9a-fA-F]{64})  (.+)$') {
            throw "Malformed package manifest line: $line"
        }
        $expected = $matches[1].ToLowerInvariant()
        $relative = $matches[2].Replace('/', [System.IO.Path]::DirectorySeparatorChar)
        $path = Join-Path $PackageRoot $relative
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Package manifest references a missing file: $relative"
        }
        $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $expected) {
            throw "Package manifest verification failed for $relative."
        }
    }
    Write-Host "Selected package manifest verified."
}

function Install-AmsOption {
    param([ValidateSet("A", "B", "C")][string]$SelectedOption)

    Assert-Python311

    $optionDirectories = @{
        "A" = "adaptive-master-subagent-orchestration-option-a-two-skill"
        "B" = "adaptive-master-subagent-orchestration-option-b-unified"
        "C" = "adaptive-master-subagent-orchestration-option-c-installer-required"
    }

    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("ams-install-" + [Guid]::NewGuid().ToString("N"))
    $archivePath = Join-Path $tempRoot $ArchiveName
    $extractPath = Join-Path $tempRoot "extracted"

    New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null
    try {
        Download-ReleaseArchive -Destination $archivePath
        New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
        Expand-Archive -LiteralPath $archivePath -DestinationPath $extractPath -Force

        $packageDirectoryName = $optionDirectories[$SelectedOption]
        $packageRootItem = Get-ChildItem -LiteralPath $extractPath -Directory -Recurse -ErrorAction Stop |
            Where-Object { $_.Name -eq $packageDirectoryName } |
            Select-Object -First 1
        if ($null -eq $packageRootItem) {
            throw "Selected package directory was not found after extraction: $packageDirectoryName"
        }
        $packageRoot = $packageRootItem.FullName
        $packageInstaller = Join-Path $packageRoot "Install-Package.ps1"

        if (-not (Test-Path -LiteralPath $packageInstaller)) {
            throw "Selected package installer was not found: $packageInstaller"
        }
        Test-PackageManifest -PackageRoot $packageRoot

        Write-Heading "Installing Option $SelectedOption"
        $installParameters = @{
            UpgradeManaged = $true
            Intensity = $Intensity
            SparkEfforts = $SparkEfforts
        }
        if ($ExcludeSpark -or $env:AMS_EXCLUDE_SPARK -eq "1") {
            $installParameters["ExcludeSpark"] = $true
        }

        & $packageInstaller @installParameters
        if ($LASTEXITCODE -ne 0) {
            throw "The selected package installer exited with code $LASTEXITCODE."
        }

        $codexHome = Get-CodexHome
        $configPath = Join-Path $codexHome "ams-orchestration.toml"
        if (Test-Path -LiteralPath $configPath) {
            $configText = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8
            if ($configText.Contains('\n')) {
                $normalized = $configText.Replace('\n', [Environment]::NewLine)
                [System.IO.File]::WriteAllText($configPath, $normalized, (New-Object System.Text.UTF8Encoding($false)))
            }
        }

        Write-Host ""
        Write-Host "Option $SelectedOption installed successfully. Restart Codex if it does not appear immediately." -ForegroundColor Green
    }
    finally {
        if (Test-Path -LiteralPath $tempRoot) {
            Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

try {
    if ([string]::IsNullOrWhiteSpace($Option) -and -not [string]::IsNullOrWhiteSpace($env:AMS_INSTALL_OPTION)) {
        $Option = $env:AMS_INSTALL_OPTION
    }
    if (-not [string]::IsNullOrWhiteSpace($env:AMS_INTENSITY)) {
        $environmentIntensity = $env:AMS_INTENSITY.Trim().ToLowerInvariant()
        if (@("auto", "minimal", "moderate", "heavy", "extreme") -notcontains $environmentIntensity) {
            throw "Unsupported AMS_INTENSITY value: $($env:AMS_INTENSITY)"
        }
        $Intensity = $environmentIntensity
    }
    if (-not [string]::IsNullOrWhiteSpace($env:AMS_SPARK_EFFORTS)) {
        $environmentSparkEfforts = @($env:AMS_SPARK_EFFORTS.Split(",") | ForEach-Object { $_.Trim().ToLowerInvariant() } | Where-Object { $_ })
        foreach ($effort in $environmentSparkEfforts) {
            if (@("low", "medium", "high") -notcontains $effort) {
                throw "Unsupported AMS_SPARK_EFFORTS value: $effort"
            }
        }
        $SparkEfforts = $environmentSparkEfforts
    }

    $selected = Get-NormalizedOption $Option
    if ($null -eq $selected) {
        $selected = Get-UserSelection
    }

    if ($selected -eq "UNINSTALL") {
        Remove-AmsInstallation
    }
    else {
        Install-AmsOption -SelectedOption $selected
    }
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
