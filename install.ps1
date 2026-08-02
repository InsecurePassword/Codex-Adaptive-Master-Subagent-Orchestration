#requires -Version 5.1

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$RepositoryOwner = "InsecurePassword"
$RepositoryName = "Codex-Adaptive-Master-Subagent-Orchestration"
$RepositoryRef = "main"
$RawBaseUrl = "https://github.com/$RepositoryOwner/$RepositoryName/raw/refs/heads/main"
$ManifestUrl = "$RawBaseUrl/install-manifest.txt"
$PackageVersion = "3.09"
$SkillName = "adaptive-master-subagent-orchestration"
$ManagedMarker = "# managed-by: adaptive-master-subagent-orchestration"
$UserAgent = "AMS-$PackageVersion-Tree-Installer"
$UserHome = if ($HOME) { $HOME } else { [Environment]::GetFolderPath("UserProfile") }
if (-not $UserHome) { throw "Unable to determine the current user home directory." }

$SkillHome = if ($env:AMS_SKILL_HOME) { $env:AMS_SKILL_HOME } else { Join-Path $UserHome ".agents\skills" }
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $UserHome ".codex" }
$Destination = Join-Path $SkillHome $SkillName
$AgentHome = Join-Path $CodexHome "agents"
$MaxManifestBytes = 256KB
$MaxFileBytes = 1MB
$MaxTotalBytes = 100MB

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

$PriorCanonicalProfileHashes = @{
    "ams_spark_low.toml" = @("b082a31f60627f4364b870c663deed670eff3c5c2adce03cb37b98452d9f0a1b")
    "ams_spark_medium.toml" = @("c387ffa3c419d66e404ebcc9a7b82a21995690a43a12350a690e9aa13dd5f45a")
    "ams_spark_high.toml" = @("bd0122c1f87b08ddb08b24df74979cf89c80c6be47627e9e0270ac2799c5320e")
}

$RequiredFiles = @(
    "SKILL.md",
    "VERSION",
    "agents/openai.yaml",
    "references/configuration-maintenance.md",
    "references/hierarchy-control.md",
    "references/intensity-control.md",
    "references/package-maintenance.md",
    "references/profile-management.md",
    "references/project-control.md",
    "references/project-governance.md",
    "references/root-execution-fallback.md",
    "references/runtime-core.md",
    "references/zergling-rush.md"
)
foreach ($ProfileFile in $ProfileFiles) {
    $RequiredFiles += "assets/agent-profiles/$ProfileFile"
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Assert-SafeDirectory {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Label
    )

    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($Item) {
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "$Label is redirected: $Path" }
        if (-not $Item.PSIsContainer) { throw "$Label is not a directory: $Path" }
        return
    }

    New-Item -ItemType Directory -Force -Path $Path | Out-Null
    $Item = Get-Item -LiteralPath $Path -Force
    if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "$Label became redirected during creation: $Path" }
}

function Invoke-WithRetry {
    param(
        [Parameter(Mandatory=$true)][ScriptBlock]$Operation,
        [Parameter(Mandatory=$true)][string]$Description
    )

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

function Invoke-Download {
    param(
        [Parameter(Mandatory=$true)][string]$Uri,
        [Parameter(Mandatory=$true)][string]$OutFile,
        [Parameter(Mandatory=$true)][string]$Description
    )

    $Headers = @{ "Accept" = "application/octet-stream"; "User-Agent" = $UserAgent }
    $null = Invoke-WithRetry -Description $Description -Operation {
        Invoke-WebRequest -UseBasicParsing -TimeoutSec 300 -Uri $Uri -Headers $Headers -OutFile $OutFile
    }
}

function Get-Sha256 {
    param([Parameter(Mandatory=$true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Read-InstallManifest {
    param([Parameter(Mandatory=$true)][string]$Path)

    $Item = Get-Item -LiteralPath $Path -Force
    if ($Item.PSIsContainer -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "Install manifest is not a safe regular file: $Path"
    }
    if ($Item.Length -le 0 -or $Item.Length -gt $MaxManifestBytes) {
        throw "Install manifest size is invalid: $($Item.Length) bytes"
    }

    $Bytes = [IO.File]::ReadAllBytes($Path)
    if ($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) {
        throw "Install manifest must be UTF-8 without BOM."
    }
    if ($Bytes[$Bytes.Length - 1] -ne 0x0A) { throw "Install manifest is missing final LF." }
    foreach ($Byte in $Bytes) {
        if ($Byte -eq 0x00 -or $Byte -eq 0x0D) { throw "Install manifest contains a forbidden NUL or CR byte." }
    }

    $Utf8 = New-Object Text.UTF8Encoding($false, $true)
    $Text = $Utf8.GetString($Bytes)
    $Lines = $Text.Split(@("`n"), [StringSplitOptions]::None)
    if ($Lines.Count -lt 4 -or $Lines[$Lines.Count - 1] -ne "") { throw "Install manifest structure is invalid." }
    if ($Lines[0] -cne "ams-install-manifest-v1") { throw "Unsupported install manifest format." }
    if ($Lines[1] -cne "version`t$PackageVersion") { throw "Install manifest version does not match $PackageVersion." }

    $Expected = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
    foreach ($Required in $RequiredFiles) { [void]$Expected.Add("$SkillName/$Required") }
    $Observed = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::Ordinal)
    $Entries = New-Object 'System.Collections.Generic.List[object]'
    [Int64]$TotalBytes = 0

    for ($Index = 2; $Index -lt $Lines.Count - 1; $Index++) {
        $Line = $Lines[$Index]
        $Fields = $Line.Split([char]"`t")
        if ($Fields.Count -ne 3) { throw "Malformed install manifest line $($Index + 1)." }
        $Hash = $Fields[0].ToLowerInvariant()
        $LengthText = $Fields[1]
        $RepoPath = $Fields[2]
        if ($Hash -notmatch '^[0-9a-f]{64}$') { throw "Invalid SHA-256 on manifest line $($Index + 1)." }
        if ($LengthText -notmatch '^[0-9]+$') { throw "Invalid byte length on manifest line $($Index + 1)." }
        [Int64]$Length = 0
        if (-not [Int64]::TryParse($LengthText, [ref]$Length) -or $Length -le 0 -or $Length -gt $MaxFileBytes) {
            throw "Unsafe byte length on manifest line $($Index + 1)."
        }
        if (-not $Expected.Contains($RepoPath) -or -not $Observed.Add($RepoPath)) {
            throw "Unexpected or duplicate install manifest path: $RepoPath"
        }
        $TotalBytes += $Length
        if ($TotalBytes -gt $MaxTotalBytes) { throw "Install manifest exceeds the total-size limit." }
        $Entries.Add([PSCustomObject]@{ Hash = $Hash; Length = $Length; RepoPath = $RepoPath })
    }

    if ($Observed.Count -ne $Expected.Count) { throw "Install manifest does not contain the exact required file set." }
    return $Entries.ToArray()
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
$Candidate = Join-Path $StageRoot $SkillName
$ManifestBefore = Join-Path $StageRoot "install-manifest.before.txt"
$ManifestAfter = Join-Path $StageRoot "install-manifest.after.txt"
$BackupPath = Join-Path $SkillHome (".{0}.backup-{1}-{2}" -f $SkillName, (Get-Date -Format "yyyyMMddHHmmss"), $PID)
$ProfileBackupRoot = Join-Path $AgentHome (".ams-profile-backup-{0}-{1}" -f $PID, [Guid]::NewGuid().ToString("N"))
$ExistingMoved = $false
$CandidateInstalled = $false
$Committed = $false
$ProfileCreated = @()
$ProfileBackups = @()
$ProfileTemps = @()

try {
    New-Item -ItemType Directory -Force -Path $Candidate, $ProfileBackupRoot | Out-Null

    Write-Host "Reading the AMS $PackageVersion install manifest from repository ref '$RepositoryRef'..."
    Invoke-Download -Uri $ManifestUrl -OutFile $ManifestBefore -Description "Install manifest download"
    $Entries = Read-InstallManifest -Path $ManifestBefore

    foreach ($Entry in $Entries) {
        $RelativePath = $Entry.RepoPath.Substring($SkillName.Length + 1)
        $TargetPath = Join-Path $Candidate $RelativePath
        $Parent = Split-Path -Parent $TargetPath
        New-Item -ItemType Directory -Force -Path $Parent | Out-Null
        $TempPath = "$TargetPath.download"
        $FileUrl = "$RawBaseUrl/$($Entry.RepoPath)"
        Invoke-Download -Uri $FileUrl -OutFile $TempPath -Description "Download of $($Entry.RepoPath)"
        $Downloaded = Get-Item -LiteralPath $TempPath -Force
        if ($Downloaded.PSIsContainer -or ($Downloaded.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Downloaded path is not a safe regular file: $($Entry.RepoPath)"
        }
        if ($Downloaded.Length -ne $Entry.Length) {
            throw "Downloaded length mismatch for $($Entry.RepoPath). Expected $($Entry.Length); received $($Downloaded.Length)."
        }
        $ActualHash = Get-Sha256 -Path $TempPath
        if ($ActualHash -cne $Entry.Hash) {
            throw "Downloaded hash mismatch for $($Entry.RepoPath)."
        }
        Move-Item -LiteralPath $TempPath -Destination $TargetPath
    }

    Invoke-Download -Uri $ManifestUrl -OutFile $ManifestAfter -Description "Final install manifest download"
    if ((Get-Item -LiteralPath $ManifestBefore).Length -ne (Get-Item -LiteralPath $ManifestAfter).Length -or
        (Get-Sha256 -Path $ManifestBefore) -cne (Get-Sha256 -Path $ManifestAfter)) {
        throw "The repository install manifest changed during download. Rerun the installer."
    }

    $ObservedVersion = (Get-Content -LiteralPath (Join-Path $Candidate "VERSION") -Raw).Trim()
    if ($ObservedVersion -cne $PackageVersion) { throw "Unexpected source version. Expected $PackageVersion; received '$ObservedVersion'." }

    foreach ($ProfileFile in $ProfileFiles) {
        $SourceProfile = Join-Path $Candidate "assets/agent-profiles/$ProfileFile"
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
        $SourceProfile = Join-Path $Destination "assets/agent-profiles/$ProfileFile"
        $TargetProfile = Join-Path $AgentHome $ProfileFile
        $TargetItem = Get-Item -LiteralPath $TargetProfile -Force -ErrorAction SilentlyContinue

        if ($TargetItem) {
            if ($TargetItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refusing to replace a redirected agent profile: $TargetProfile" }
            if ($TargetItem.PSIsContainer) { throw "Agent profile target is not a regular file: $TargetProfile" }
            $SourceHash = Get-Sha256 -Path $SourceProfile
            $TargetHash = Get-Sha256 -Path $TargetProfile
            if ($SourceHash -ceq $TargetHash) {
                $ProfilesUnchanged++
                continue
            }

            $AuthorizedPriorHashes = @()
            if ($PriorCanonicalProfileHashes.ContainsKey($ProfileFile)) {
                $AuthorizedPriorHashes = @($PriorCanonicalProfileHashes[$ProfileFile])
            }
            if ($AuthorizedPriorHashes -notcontains $TargetHash) {
                throw "Refusing to replace a differing profile without exact official provenance: $TargetProfile. Review, rename, remove, or manually reconcile it before retrying."
            }
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
        $SourceHash = Get-Sha256 -Path $SourceProfile
        if ((Get-Sha256 -Path $TempProfile) -cne $SourceHash) { throw "Agent profile staging verification failed: $ProfileFile" }
        Move-Item -LiteralPath $TempProfile -Destination $TargetProfile
        if ((Get-Sha256 -Path $TargetProfile) -cne $SourceHash) { throw "Agent profile installation verification failed: $ProfileFile" }
        $ProfilesChanged++
    }

    $Committed = $true

    if ($ExistingMoved) {
        Remove-Item -LiteralPath $BackupPath -Recurse -Force -ErrorAction SilentlyContinue
        $ExistingMoved = $false
    }
    Remove-Item -LiteralPath $ProfileBackupRoot -Recurse -Force -ErrorAction SilentlyContinue

    Write-Host "Installed Adaptive Master-Subagent Orchestration $PackageVersion directly from the repository tree."
    Write-Host "Repository ref: $RepositoryRef"
    Write-Host "Skill: $Destination"
    Write-Host "Profiles: $AgentHome ($ProfilesChanged changed, $ProfilesUnchanged unchanged)"
    Write-Host "Restart or reload Codex before using the updated skill or profiles."
}
finally {
    if (-not $Committed) {
        foreach ($TempProfile in $ProfileTemps) {
            Remove-Item -LiteralPath $TempProfile -Force -ErrorAction SilentlyContinue
        }
        foreach ($CreatedProfile in $ProfileCreated) {
            Remove-Item -LiteralPath $CreatedProfile -Force -ErrorAction SilentlyContinue
        }
        for ($Index = $ProfileBackups.Count - 1; $Index -ge 0; $Index--) {
            $Record = $ProfileBackups[$Index]
            Remove-Item -LiteralPath $Record.Target -Force -ErrorAction SilentlyContinue
            if (Test-Path -LiteralPath $Record.Backup -PathType Leaf) {
                Move-Item -LiteralPath $Record.Backup -Destination $Record.Target -ErrorAction SilentlyContinue
            }
        }
        if ($CandidateInstalled -and (Test-Path -LiteralPath $Destination -PathType Container)) {
            Remove-Item -LiteralPath $Destination -Recurse -Force -ErrorAction SilentlyContinue
        }
        if ($ExistingMoved -and -not (Test-Path -LiteralPath $Destination) -and (Test-Path -LiteralPath $BackupPath -PathType Container)) {
            Move-Item -LiteralPath $BackupPath -Destination $Destination -ErrorAction SilentlyContinue
        }
    }

    Remove-Item -LiteralPath $ProfileBackupRoot -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $StageRoot -Recurse -Force -ErrorAction SilentlyContinue
    if ($LockStream) { $LockStream.Dispose() }
    Remove-Item -LiteralPath $LockPath -Force -ErrorAction SilentlyContinue
}
