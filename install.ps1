#requires -Version 5.1

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$ReleaseUrl = if ($env:AMS_RELEASE_URL) {
    $env:AMS_RELEASE_URL
}
else {
    "https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/releases/download/ReleaseZip/adaptive-master-subagent-orchestration-3.08.zip"
}
$ExpectedSha256 = if ($env:AMS_EXPECTED_SHA256) {
    $env:AMS_EXPECTED_SHA256.Trim().ToLowerInvariant()
}
else {
    "e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6"
}
$SkillName = "adaptive-master-subagent-orchestration"
$UserHome = if ($HOME) { $HOME } else { [Environment]::GetFolderPath("UserProfile") }
$SkillHome = if ($env:AMS_SKILL_HOME) { $env:AMS_SKILL_HOME } else { Join-Path $UserHome ".agents\skills" }
$Destination = Join-Path $SkillHome $SkillName
$RequiredFiles = @(
    "SKILL.md",
    "VERSION",
    "agents/openai.yaml",
    "references/intensity-control.md",
    "references/package-maintenance.md",
    "references/profile-management.md",
    "references/project-control.md",
    "references/runtime-core.md",
    "references/zergling-rush.md"
)

if (-not $UserHome) {
    throw "Unable to determine the current user home directory."
}
if ($ExpectedSha256 -notmatch '^[0-9a-f]{64}$') {
    throw "AMS_EXPECTED_SHA256 must contain exactly 64 hexadecimal characters."
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
New-Item -ItemType Directory -Force -Path $SkillHome | Out-Null

$StageRoot = Join-Path $SkillHome (".ams-install-{0}-{1}" -f $PID, [Guid]::NewGuid().ToString("N"))
$ArchivePath = Join-Path $StageRoot "package.zip"
$ExtractRoot = Join-Path $StageRoot "extract"
$BackupPath = Join-Path $SkillHome (".{0}.backup-{1}-{2}" -f $SkillName, (Get-Date -Format "yyyyMMddHHmmss"), $PID)
$ExistingMoved = $false

function Remove-Stage {
    if (Test-Path -LiteralPath $StageRoot) {
        Remove-Item -LiteralPath $StageRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

try {
    New-Item -ItemType Directory -Force -Path $StageRoot, $ExtractRoot | Out-Null

    $Headers = @{
        "Accept"     = "application/octet-stream"
        "User-Agent" = "AMS-3.08-Installer"
    }
    if ($env:GITHUB_TOKEN) {
        $Headers["Authorization"] = "Bearer $($env:GITHUB_TOKEN)"
    }

    Write-Host "Downloading Adaptive Master-Subagent Orchestration 3.08..."
    try {
        Invoke-WebRequest -UseBasicParsing -Uri $ReleaseUrl -Headers $Headers -OutFile $ArchivePath
    }
    catch {
        $Hint = if ($env:GITHUB_TOKEN) {
            "Verify the release URL and that GITHUB_TOKEN can read the repository."
        }
        else {
            "If the repository or release is private, set GITHUB_TOKEN to a token with repository read access."
        }
        throw "Release download failed. $Hint`n$($_.Exception.Message)"
    }

    if (-not (Test-Path -LiteralPath $ArchivePath -PathType Leaf) -or (Get-Item -LiteralPath $ArchivePath).Length -eq 0) {
        throw "The release download was empty."
    }

    $ActualSha256 = (Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($ActualSha256 -ne $ExpectedSha256) {
        throw "Release checksum mismatch. Expected $ExpectedSha256; received $ActualSha256."
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $Archive = [IO.Compression.ZipFile]::OpenRead($ArchivePath)
    try {
        if ($Archive.Entries.Count -eq 0 -or $Archive.Entries.Count -gt 500) {
            throw "The release archive has an invalid entry count: $($Archive.Entries.Count)."
        }

        [Int64]$ExpandedBytes = 0
        $Names = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
        foreach ($Entry in $Archive.Entries) {
            $Name = $Entry.FullName.Replace('\', '/')
            if ([string]::IsNullOrWhiteSpace($Name) -or
                $Name.StartsWith('/') -or
                $Name -match '^[A-Za-z]:' -or
                $Name.Contains("`0") -or
                $Name -notlike "$SkillName/*") {
                throw "The release archive contains an unsafe or unexpected path: $Name"
            }

            $Parts = $Name.Split('/')
            if ($Parts -contains '..') {
                throw "The release archive contains path traversal: $Name"
            }
            if (-not $Names.Add($Name.TrimEnd('/'))) {
                throw "The release archive contains a duplicate path: $Name"
            }

            $ExternalAttributes = [BitConverter]::ToUInt32([BitConverter]::GetBytes([Int32]$Entry.ExternalAttributes), 0)
            $UnixMode = ($ExternalAttributes -shr 16) -band 0xF000
            if ($UnixMode -eq 0xA000) {
                throw "The release archive contains an unsupported symbolic link: $Name"
            }

            $ExpandedBytes += $Entry.Length
            if ($ExpandedBytes -gt 104857600) {
                throw "The expanded release exceeds the 100 MiB safety limit."
            }
        }

        foreach ($Required in $RequiredFiles) {
            $ArchiveName = "$SkillName/$Required"
            if (-not $Names.Contains($ArchiveName)) {
                throw "The release archive is missing required file: $ArchiveName"
            }
        }
    }
    finally {
        $Archive.Dispose()
    }

    Expand-Archive -LiteralPath $ArchivePath -DestinationPath $ExtractRoot -Force
    $Candidate = Join-Path $ExtractRoot $SkillName
    if (-not (Test-Path -LiteralPath $Candidate -PathType Container)) {
        throw "The extracted package root was not found: $Candidate"
    }

    foreach ($Required in $RequiredFiles) {
        $RequiredPath = Join-Path $Candidate ($Required -replace '/', '\')
        if (-not (Test-Path -LiteralPath $RequiredPath -PathType Leaf)) {
            throw "The extracted package is missing required file: $Required"
        }
        $Item = Get-Item -LiteralPath $RequiredPath -Force
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "The extracted package contains a redirected required file: $Required"
        }
    }

    if (Test-Path -LiteralPath $Destination) {
        $Existing = Get-Item -LiteralPath $Destination -Force
        if ($Existing.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Refusing to replace a redirected existing skill path: $Destination"
        }
        if (Test-Path -LiteralPath $BackupPath) {
            throw "Unexpected backup collision: $BackupPath"
        }
        Move-Item -LiteralPath $Destination -Destination $BackupPath
        $ExistingMoved = $true
    }

    try {
        Move-Item -LiteralPath $Candidate -Destination $Destination
    }
    catch {
        if ($ExistingMoved -and -not (Test-Path -LiteralPath $Destination) -and (Test-Path -LiteralPath $BackupPath)) {
            Move-Item -LiteralPath $BackupPath -Destination $Destination
            $ExistingMoved = $false
        }
        throw
    }

    if ($ExistingMoved -and (Test-Path -LiteralPath $BackupPath)) {
        Remove-Item -LiteralPath $BackupPath -Recurse -Force
    }

    Write-Host "Installed Adaptive Master-Subagent Orchestration 3.08 to:"
    Write-Host "  $Destination"
    Write-Host "Restart or reload Codex before using the updated skill."
}
finally {
    Remove-Stage
}
