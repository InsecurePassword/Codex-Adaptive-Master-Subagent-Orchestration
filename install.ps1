#requires -Version 5.1

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$RepositoryOwner = "InsecurePassword"
$RepositoryName = "Codex-Adaptive-Master-Subagent-Orchestration"
$PackageVersion = "3.09"
$ReleaseTag = "ReleaseZip"
$AssetName = "adaptive-master-subagent-orchestration-$PackageVersion.zip"
$DefaultReleaseUrl = "https://github.com/$RepositoryOwner/$RepositoryName/releases/download/$ReleaseTag/$AssetName"
$ReleaseUrl = if ($env:AMS_RELEASE_URL) { $env:AMS_RELEASE_URL } else { $DefaultReleaseUrl }
$ExpectedSha256 = if ($env:AMS_EXPECTED_SHA256) { $env:AMS_EXPECTED_SHA256.Trim().ToLowerInvariant() } else { "f35aa28cad7c2691e80823e36ca276cbee8b20de067600fd8edb8f2aaf10fe4b" }
$UserAgent = "AMS-$PackageVersion-Installer"
$SkillName = "adaptive-master-subagent-orchestration"
$ManagedMarker = "# managed-by: adaptive-master-subagent-orchestration"
$UserHome = if ($HOME) { $HOME } else { [Environment]::GetFolderPath("UserProfile") }
if (-not $UserHome) { throw "Unable to determine the current user home directory." }
$SkillHome = if ($env:AMS_SKILL_HOME) { $env:AMS_SKILL_HOME } else { Join-Path $UserHome ".agents\skills" }
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $UserHome ".codex" }
$Destination = Join-Path $SkillHome $SkillName
$AgentHome = Join-Path $CodexHome "agents"
$MaxArchiveBytes = 10MB
$MaxExpandedBytes = 100MB

$ProfileFiles = @(
    "ams_sol_low.toml",
    "ams_sol_medium.toml",
    "ams_sol_high.toml",
    "ams_sol_xhigh.toml",
    "ams_sol_max.toml",
    "ams_terra_low.toml",
    "ams_terra_medium.toml",
    "ams_terra_high.toml",
    "ams_terra_xhigh.toml",
    "ams_terra_max.toml",
    "ams_luna_low.toml",
    "ams_luna_medium.toml",
    "ams_luna_high.toml",
    "ams_luna_xhigh.toml",
    "ams_luna_max.toml",
    "ams_spark_low.toml",
    "ams_spark_medium.toml",
    "ams_spark_high.toml"
)

$RequiredFiles = @(
    "SKILL.md",
    "VERSION",
    "agents/openai.yaml",
    "references/hierarchy-control.md",
    "references/intensity-control.md",
    "references/package-maintenance.md",
    "references/profile-management.md",
    "references/project-control.md",
    "references/runtime-core.md",
    "references/zergling-rush.md"
)
foreach ($ProfileFile in $ProfileFiles) {
    $RequiredFiles += "assets/agent-profiles/$ProfileFile"
}

if ($ExpectedSha256 -notmatch '^[0-9a-f]{64}$') { throw "AMS_EXPECTED_SHA256 must contain exactly 64 hexadecimal characters." }
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Assert-SafeDirectory {
    param([Parameter(Mandatory=$true)][string]$Path, [Parameter(Mandatory=$true)][string]$Label)
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($Item) {
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "$Label is redirected: $Path" }
        if (-not $Item.PSIsContainer) { throw "$Label is not a directory: $Path" }
    }
    else {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
        $Item = Get-Item -LiteralPath $Path -Force
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "$Label became redirected during creation: $Path" }
    }
}

Assert-SafeDirectory -Path $SkillHome -Label "Skill parent"
Assert-SafeDirectory -Path $CodexHome -Label "CODEX_HOME"
Assert-SafeDirectory -Path $AgentHome -Label "Agent registry"

$LockPath = Join-Path $SkillHome ".$SkillName.install.lock"
$LockStream = $null
if (Test-Path -LiteralPath $LockPath) {
    $LockItem = Get-Item -LiteralPath $LockPath -Force
    if ($LockItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Installer lock path is redirected: $LockPath" }
}
try {
    $LockStream = [IO.File]::Open($LockPath, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    $LockStream.SetLength(0)
    $LockBytes = [Text.Encoding]::UTF8.GetBytes("pid=$PID")
    $LockStream.Write($LockBytes, 0, $LockBytes.Length)
    $LockStream.Flush()
}
catch {
    throw "Another installation is active or the installer lock cannot be acquired: $LockPath`n$($_.Exception.Message)"
}

$StageRoot = Join-Path $SkillHome (".ams-install-{0}-{1}" -f $PID, [Guid]::NewGuid().ToString("N"))
$ArchivePath = Join-Path $StageRoot "package.zip"
$ExtractRoot = Join-Path $StageRoot "extract"
$BackupPath = Join-Path $SkillHome (".{0}.backup-{1}-{2}" -f $SkillName, (Get-Date -Format "yyyyMMddHHmmss"), $PID)
$ProfileBackupRoot = Join-Path $AgentHome (".ams-profile-backup-{0}-{1}" -f $PID, [Guid]::NewGuid().ToString("N"))
$ExistingMoved = $false
$CandidateInstalled = $false
$Committed = $false
$ProfileCreated = @()
$ProfileBackups = @()
$ProfileTemps = @()

function Invoke-WithRetry {
    param([ScriptBlock]$Operation, [string]$Description)
    $LastError = $null
    foreach ($Attempt in 1..3) {
        try { return (& $Operation) }
        catch {
            $LastError = $_
            if ($Attempt -lt 3) { Start-Sleep -Seconds $Attempt }
        }
    }
    throw "$Description failed after 3 attempts.`n$($LastError.Exception.Message)"
}

function Get-DownloadTarget {
    if ($env:AMS_RELEASE_URL -or -not $env:GITHUB_TOKEN) {
        return [PSCustomObject]@{ Uri = $ReleaseUrl; Api = $false }
    }
    $MetadataUri = "https://api.github.com/repos/$RepositoryOwner/$RepositoryName/releases/tags/$ReleaseTag"
    $MetadataHeaders = @{
        "Accept" = "application/vnd.github+json"
        "Authorization" = "Bearer $($env:GITHUB_TOKEN)"
        "User-Agent" = $UserAgent
        "X-GitHub-Api-Version" = "2022-11-28"
    }
    $Response = Invoke-WithRetry -Description "Release metadata lookup" -Operation {
        Invoke-WebRequest -UseBasicParsing -TimeoutSec 60 -Uri $MetadataUri -Headers $MetadataHeaders
    }
    $Release = $Response.Content | ConvertFrom-Json
    $Asset = @($Release.assets) | Where-Object { $_.name -ceq $AssetName } | Select-Object -First 1
    if (-not $Asset -or -not $Asset.url) { throw "Release asset '$AssetName' was not found in tag '$ReleaseTag'." }
    return [PSCustomObject]@{ Uri = [string]$Asset.url; Api = $true }
}

try {
    New-Item -ItemType Directory -Force -Path $StageRoot, $ExtractRoot, $ProfileBackupRoot | Out-Null
    $Target = Get-DownloadTarget
    $Headers = @{ "Accept" = "application/octet-stream"; "User-Agent" = $UserAgent }
    if ($env:GITHUB_TOKEN) {
        $Headers["Authorization"] = "Bearer $($env:GITHUB_TOKEN)"
        $Headers["X-GitHub-Api-Version"] = "2022-11-28"
    }

    Write-Host "Downloading Adaptive Master-Subagent Orchestration $PackageVersion..."
    try {
        $null = Invoke-WithRetry -Description "Release download" -Operation {
            Invoke-WebRequest -UseBasicParsing -TimeoutSec 300 -Uri $Target.Uri -Headers $Headers -OutFile $ArchivePath
        }
    }
    catch {
        $Hint = if ($env:GITHUB_TOKEN) { "Verify the release and GITHUB_TOKEN repository read access." } else { "If access is private, set GITHUB_TOKEN to a token with repository read access." }
        throw "Release download failed. $Hint`n$($_.Exception.Message)"
    }

    if (-not (Test-Path -LiteralPath $ArchivePath -PathType Leaf)) { throw "The release download is missing." }
    $ArchiveItem = Get-Item -LiteralPath $ArchivePath
    if ($ArchiveItem.Length -eq 0) { throw "The release download was empty." }
    if ($ArchiveItem.Length -gt $MaxArchiveBytes) { throw "The compressed release exceeds the 10 MiB safety limit." }
    $ActualSha256 = (Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($ActualSha256 -ne $ExpectedSha256) { throw "Release checksum mismatch. Expected $ExpectedSha256; received $ActualSha256." }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $Archive = [IO.Compression.ZipFile]::OpenRead($ArchivePath)
    try {
        $ExpectedNames = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
        foreach ($Required in $RequiredFiles) { [void]$ExpectedNames.Add("$SkillName/$Required") }
        $AllowedDirectories = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
        foreach ($DirectoryName in @("$SkillName/", "$SkillName/agents/", "$SkillName/assets/", "$SkillName/assets/agent-profiles/", "$SkillName/references/")) {
            [void]$AllowedDirectories.Add($DirectoryName)
        }
        $ObservedNames = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
        $ObservedDirectories = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
        [Int64]$ExpandedBytes = 0
        $Buffer = New-Object byte[] 81920
        foreach ($Entry in $Archive.Entries) {
            $Name = $Entry.FullName
            $ExternalAttributes = [BitConverter]::ToUInt32([BitConverter]::GetBytes([Int32]$Entry.ExternalAttributes), 0)
            if ((($ExternalAttributes -shr 16) -band 0xF000) -eq 0xA000) { throw "The release archive contains an unsupported symbolic link: $Name" }
            if ($Name.EndsWith('/')) {
                if ($Entry.Length -ne 0 -or -not $AllowedDirectories.Contains($Name) -or -not $ObservedDirectories.Add($Name)) {
                    throw "The release archive contains an unexpected or duplicate directory entry: $Name"
                }
                continue
            }
            if (-not $ExpectedNames.Contains($Name) -or -not $ObservedNames.Add($Name)) { throw "The release archive file set does not exactly match the $PackageVersion package contract: $Name" }
            $ExpandedBytes += $Entry.Length
            if ($ExpandedBytes -gt $MaxExpandedBytes) { throw "The expanded release exceeds the 100 MiB safety limit." }
            $Stream = $null
            try {
                $Stream = $Entry.Open()
                [Int64]$ReadTotal = 0
                while (($Read = $Stream.Read($Buffer, 0, $Buffer.Length)) -gt 0) { $ReadTotal += $Read }
                if ($ReadTotal -ne $Entry.Length) { throw "The release archive entry failed integrity validation: $Name" }
            }
            finally { if ($Stream) { $Stream.Dispose() } }
        }
        if ($ObservedNames.Count -ne $ExpectedNames.Count) { throw "The release archive is missing required files." }
    }
    finally { $Archive.Dispose() }

    Expand-Archive -LiteralPath $ArchivePath -DestinationPath $ExtractRoot -Force
    $Candidate = Join-Path $ExtractRoot $SkillName
    if (-not (Test-Path -LiteralPath $Candidate -PathType Container)) { throw "The extracted package root was not found: $Candidate" }
    $CandidateItem = Get-Item -LiteralPath $Candidate -Force
    if ($CandidateItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "The extracted package root is redirected." }

    $ObservedExtracted = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
    foreach ($File in Get-ChildItem -LiteralPath $Candidate -File -Recurse -Force) {
        if ($File.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "The extracted package contains a redirected file: $($File.FullName)" }
        $Relative = $File.FullName.Substring($Candidate.Length).TrimStart([char[]]@('\','/')).Replace('\','/')
        [void]$ObservedExtracted.Add("$SkillName/$Relative")
    }
    if ($ObservedExtracted.Count -ne $RequiredFiles.Count) { throw "The extracted package file count does not match the $PackageVersion package contract." }
    foreach ($Required in $RequiredFiles) {
        if (-not $ObservedExtracted.Contains("$SkillName/$Required")) { throw "The extracted package is missing required file: $Required" }
    }

    $ObservedVersion = (Get-Content -LiteralPath (Join-Path $Candidate "VERSION") -Raw).Trim()
    if ($ObservedVersion -cne $PackageVersion) { throw "Unexpected package version. Expected $PackageVersion; received '$ObservedVersion'." }

    foreach ($ProfileFile in $ProfileFiles) {
        $SourceProfile = Join-Path $Candidate "assets\agent-profiles\$ProfileFile"
        $SourceItem = Get-Item -LiteralPath $SourceProfile -Force -ErrorAction SilentlyContinue
        if (-not $SourceItem -or $SourceItem.PSIsContainer -or ($SourceItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Bundled profile is missing or redirected: $ProfileFile"
        }
        $FirstLine = @(Get-Content -LiteralPath $SourceProfile -TotalCount 1)[0]
        if ($FirstLine -cne $ManagedMarker) { throw "Bundled profile lacks the required managed marker: $ProfileFile" }
    }

    $Existing = Get-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
    if ($Existing) {
        if ($Existing.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refusing to replace a redirected existing skill path: $Destination" }
        if (-not $Existing.PSIsContainer) { throw "Refusing to replace a non-directory existing skill path: $Destination" }
        if (Test-Path -LiteralPath $BackupPath) { throw "Unexpected backup collision: $BackupPath" }
        Move-Item -LiteralPath $Destination -Destination $BackupPath
        $ExistingMoved = $true
    }

    Move-Item -LiteralPath $Candidate -Destination $Destination
    $CandidateInstalled = $true

    $ProfilesChanged = 0
    $ProfilesUnchanged = 0
    foreach ($ProfileFile in $ProfileFiles) {
        $SourceProfile = Join-Path $Destination "assets\agent-profiles\$ProfileFile"
        $TargetProfile = Join-Path $AgentHome $ProfileFile
        $TargetItem = Get-Item -LiteralPath $TargetProfile -Force -ErrorAction SilentlyContinue

        if ($TargetItem) {
            if ($TargetItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refusing to replace a redirected agent profile: $TargetProfile" }
            if ($TargetItem.PSIsContainer) { throw "Agent profile target is not a regular file: $TargetProfile" }
            $SourceHash = (Get-FileHash -LiteralPath $SourceProfile -Algorithm SHA256).Hash
            $TargetHash = (Get-FileHash -LiteralPath $TargetProfile -Algorithm SHA256).Hash
            if ($SourceHash -ceq $TargetHash) {
                $ProfilesUnchanged++
                continue
            }

            $FirstLine = @(Get-Content -LiteralPath $TargetProfile -TotalCount 1)[0]
            if ($FirstLine -cne $ManagedMarker) { throw "Refusing to overwrite an unrecognized or user-authored profile: $TargetProfile" }
            $SavedProfile = Join-Path $ProfileBackupRoot $ProfileFile
            Move-Item -LiteralPath $TargetProfile -Destination $SavedProfile
            $ProfileBackups += [PSCustomObject]@{ Target = $TargetProfile; Backup = $SavedProfile }
        }
        else {
            $ProfileCreated += $TargetProfile
        }

        $TempProfile = Join-Path $AgentHome (".{0}.ams-install.{1}" -f $ProfileFile, [Guid]::NewGuid().ToString("N"))
        $ProfileTemps += $TempProfile
        Copy-Item -LiteralPath $SourceProfile -Destination $TempProfile
        $SourceHash = (Get-FileHash -LiteralPath $SourceProfile -Algorithm SHA256).Hash
        $TempHash = (Get-FileHash -LiteralPath $TempProfile -Algorithm SHA256).Hash
        if ($SourceHash -cne $TempHash) { throw "Agent profile staging verification failed: $ProfileFile" }
        Move-Item -LiteralPath $TempProfile -Destination $TargetProfile
        $TargetHash = (Get-FileHash -LiteralPath $TargetProfile -Algorithm SHA256).Hash
        if ($SourceHash -cne $TargetHash) { throw "Agent profile installation verification failed: $ProfileFile" }
        $ProfilesChanged++
    }

    $Committed = $true

    if ($ExistingMoved) {
        Remove-Item -LiteralPath $BackupPath -Recurse -Force -ErrorAction SilentlyContinue
        $ExistingMoved = $false
    }
    Remove-Item -LiteralPath $ProfileBackupRoot -Recurse -Force -ErrorAction SilentlyContinue
    $ProfileBackupRoot = $null

    Write-Host "Installed Adaptive Master-Subagent Orchestration $PackageVersion to:"
    Write-Host "  $Destination"
    Write-Host "Installed or updated $ProfilesChanged AMS profiles; $ProfilesUnchanged were already current."
    Write-Host "Agent profile registry:"
    Write-Host "  $AgentHome"
    Write-Host "Restart or reload Codex before using the updated skill and profiles."
}
catch {
    if (-not $Committed) {
        foreach ($TempProfile in $ProfileTemps) {
            if ($TempProfile -and (Test-Path -LiteralPath $TempProfile -PathType Leaf)) {
                Remove-Item -LiteralPath $TempProfile -Force -ErrorAction SilentlyContinue
            }
        }
        foreach ($CreatedProfile in $ProfileCreated) {
            if ($CreatedProfile -and (Test-Path -LiteralPath $CreatedProfile -PathType Leaf)) {
                Remove-Item -LiteralPath $CreatedProfile -Force -ErrorAction SilentlyContinue
            }
        }
        for ($Index = $ProfileBackups.Count - 1; $Index -ge 0; $Index--) {
            $Record = $ProfileBackups[$Index]
            Remove-Item -LiteralPath $Record.Target -Force -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $Record.Backup -PathType Leaf) {
                Move-Item -LiteralPath $Record.Backup -Destination $Record.Target -Force -ErrorAction SilentlyContinue
            }
        }
        if ($CandidateInstalled -and (Test-Path -LiteralPath $Destination -PathType Container)) {
            Remove-Item -LiteralPath $Destination -Recurse -Force -ErrorAction SilentlyContinue
        }
        if ($ExistingMoved -and -not (Test-Path -LiteralPath $Destination) -and (Test-Path -LiteralPath $BackupPath -PathType Container)) {
            Move-Item -LiteralPath $BackupPath -Destination $Destination -ErrorAction SilentlyContinue
        }
    }
    throw
}
finally {
    if ($ProfileBackupRoot -and (Test-Path -LiteralPath $ProfileBackupRoot -PathType Container)) {
        Remove-Item -LiteralPath $ProfileBackupRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path -LiteralPath $StageRoot) { Remove-Item -LiteralPath $StageRoot -Recurse -Force -ErrorAction SilentlyContinue }
    if ($LockStream) { $LockStream.Dispose() }
    Remove-Item -LiteralPath $LockPath -Force -ErrorAction SilentlyContinue
}
