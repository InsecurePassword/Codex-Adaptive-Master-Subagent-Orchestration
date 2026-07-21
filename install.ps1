#requires -Version 5.1

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$RepositoryOwner = "InsecurePassword"
$RepositoryName = "Codex-Adaptive-Master-Subagent-Orchestration"
$ReleaseTag = "ReleaseZip"
$AssetName = "adaptive-master-subagent-orchestration-3.08.zip"
$DefaultReleaseUrl = "https://github.com/$RepositoryOwner/$RepositoryName/releases/download/$ReleaseTag/$AssetName"
$ReleaseUrl = if ($env:AMS_RELEASE_URL) { $env:AMS_RELEASE_URL } else { $DefaultReleaseUrl }
$ExpectedSha256 = if ($env:AMS_EXPECTED_SHA256) { $env:AMS_EXPECTED_SHA256.Trim().ToLowerInvariant() } else { "e45eed1762ed24d1a0f671d9fb7424558694f0bef557aaca97f0cc0828d07be6" }
$SkillName = "adaptive-master-subagent-orchestration"
$UserHome = if ($HOME) { $HOME } else { [Environment]::GetFolderPath("UserProfile") }
if (-not $UserHome) { throw "Unable to determine the current user home directory." }
$SkillHome = if ($env:AMS_SKILL_HOME) { $env:AMS_SKILL_HOME } else { Join-Path $UserHome ".agents\skills" }
$Destination = Join-Path $SkillHome $SkillName
$MaxArchiveBytes = 10MB
$MaxExpandedBytes = 100MB
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

if ($ExpectedSha256 -notmatch '^[0-9a-f]{64}$') { throw "AMS_EXPECTED_SHA256 must contain exactly 64 hexadecimal characters." }
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
New-Item -ItemType Directory -Force -Path $SkillHome | Out-Null

$LockPath = Join-Path $SkillHome ".$SkillName.install.lock"
$LockStream = $null
if (Test-Path -LiteralPath $LockPath) {
    $LockItem = Get-Item -LiteralPath $LockPath -Force
    if ($LockItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Installer lock path is redirected: $LockPath" }
}
try {
    $LockStream = [IO.File]::Open($LockPath, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    $LockStream.SetLength(0)
    $LockWriter = New-Object -TypeName IO.StreamWriter -ArgumentList $LockStream, [Text.Encoding]::UTF8, 1024, $true
    $LockWriter.Write("pid=$PID")
    $LockWriter.Flush()
    $LockWriter.Dispose()
}
catch {
    throw "Another installation is active or the installer lock cannot be acquired: $LockPath`n$($_.Exception.Message)"
}

$StageRoot = Join-Path $SkillHome (".ams-install-{0}-{1}" -f $PID, [Guid]::NewGuid().ToString("N"))
$ArchivePath = Join-Path $StageRoot "package.zip"
$ExtractRoot = Join-Path $StageRoot "extract"
$BackupPath = Join-Path $SkillHome (".{0}.backup-{1}-{2}" -f $SkillName, (Get-Date -Format "yyyyMMddHHmmss"), $PID)
$ExistingMoved = $false
$CandidateInstalled = $false
$Committed = $false

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
        "User-Agent" = "AMS-3.08-Installer"
        "X-GitHub-Api-Version" = "2022-11-28"
    }
    $Response = Invoke-WithRetry -Description "Private release metadata lookup" -Operation {
        Invoke-WebRequest -UseBasicParsing -TimeoutSec 60 -Uri $MetadataUri -Headers $MetadataHeaders
    }
    $Release = $Response.Content | ConvertFrom-Json
    $Asset = @($Release.assets) | Where-Object { $_.name -ceq $AssetName } | Select-Object -First 1
    if (-not $Asset -or -not $Asset.url) { throw "Release asset '$AssetName' was not found in tag '$ReleaseTag'." }
    return [PSCustomObject]@{ Uri = [string]$Asset.url; Api = $true }
}

try {
    New-Item -ItemType Directory -Force -Path $StageRoot, $ExtractRoot | Out-Null
    $Target = Get-DownloadTarget
    $Headers = @{ "Accept" = "application/octet-stream"; "User-Agent" = "AMS-3.08-Installer" }
    if ($env:GITHUB_TOKEN) {
        $Headers["Authorization"] = "Bearer $($env:GITHUB_TOKEN)"
        $Headers["X-GitHub-Api-Version"] = "2022-11-28"
    }

    Write-Host "Downloading Adaptive Master-Subagent Orchestration 3.08..."
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
        if ($Archive.Entries.Count -ne $RequiredFiles.Count) { throw "The release archive entry count does not match the 3.08 package contract." }
        $ExpectedNames = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
        foreach ($Required in $RequiredFiles) { [void]$ExpectedNames.Add("$SkillName/$Required") }
        $ObservedNames = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
        [Int64]$ExpandedBytes = 0
        $Buffer = New-Object byte[] 81920
        foreach ($Entry in $Archive.Entries) {
            $Name = $Entry.FullName
            if (-not $ExpectedNames.Contains($Name) -or -not $ObservedNames.Add($Name)) { throw "The release archive file set does not exactly match the 3.08 package contract: $Name" }
            $ExternalAttributes = [BitConverter]::ToUInt32([BitConverter]::GetBytes([Int32]$Entry.ExternalAttributes), 0)
            if ((($ExternalAttributes -shr 16) -band 0xF000) -eq 0xA000) { throw "The release archive contains an unsupported symbolic link: $Name" }
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
    if ($ObservedExtracted.Count -ne $RequiredFiles.Count) { throw "The extracted package file count does not match the 3.08 package contract." }
    foreach ($Required in $RequiredFiles) {
        if (-not $ObservedExtracted.Contains("$SkillName/$Required")) { throw "The extracted package is missing required file: $Required" }
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
    if ($ExistingMoved) {
        Remove-Item -LiteralPath $BackupPath -Recurse -Force
        $ExistingMoved = $false
    }
    $Committed = $true

    Write-Host "Installed Adaptive Master-Subagent Orchestration 3.08 to:"
    Write-Host "  $Destination"
    Write-Host "Restart or reload Codex before using the updated skill."
}
catch {
    if (-not $Committed) {
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
    if (Test-Path -LiteralPath $StageRoot) { Remove-Item -LiteralPath $StageRoot -Recurse -Force -ErrorAction SilentlyContinue }
    if ($LockStream) { $LockStream.Dispose() }
    Remove-Item -LiteralPath $LockPath -Force -ErrorAction SilentlyContinue
}
