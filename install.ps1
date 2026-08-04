#requires -Version 5.1

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$RepositoryOwner = "InsecurePassword"
$RepositoryName = "Codex-Adaptive-Master-Subagent-Orchestration"
$RepositoryRef = "main"
$RawBaseUrl = "https://github.com/$RepositoryOwner/$RepositoryName/raw/refs/heads/main"
$ManifestUrl = "$RawBaseUrl/install-manifest.txt"
$PackageVersion = "4.0"
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
$MaxRuntimeBytes = 64MB
$MaxRuntimeRecordBytes = 64KB
$MaxRuntimeFiles = 2048

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
    "references/convergence-control.md",
    "references/evidence-handling.md",
    "references/feature-control.md",
    "references/handoff-control.md",
    "references/hierarchy-control.md",
    "references/intensity-control.md",
    "references/package-maintenance.md",
    "references/profile-management.md",
    "references/project-control.md",
    "references/project-governance.md",
    "references/request-accounting.md",
    "references/review-control.md",
    "references/root-execution-fallback.md",
    "references/runtime-core.md",
    "references/runtime-observation.md",
    "references/shared-worktree-control.md",
    "references/surface-identity.md",
    "references/task-graph-safeguards.md",
    "references/work-order-refinement.md",
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


function Get-RuntimeAllowedSids {
    return @(
        [Security.Principal.WindowsIdentity]::GetCurrent().User,
        (New-Object -TypeName Security.Principal.SecurityIdentifier -ArgumentList 'S-1-5-18'),
        (New-Object -TypeName Security.Principal.SecurityIdentifier -ArgumentList 'S-1-5-32-544')
    )
}

function Set-OwnerOnlyRuntimeAccess {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][bool]$Directory
    )
    $Current = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $Allowed = @(Get-RuntimeAllowedSids)
    if ($Directory) {
        $Acl = New-Object Security.AccessControl.DirectorySecurity
        $Inheritance = [Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [Security.AccessControl.InheritanceFlags]::ObjectInherit
        foreach ($Sid in $Allowed) {
            $Rule = New-Object Security.AccessControl.FileSystemAccessRule($Sid, [Security.AccessControl.FileSystemRights]::FullControl, $Inheritance, [Security.AccessControl.PropagationFlags]::None, [Security.AccessControl.AccessControlType]::Allow)
            [void]$Acl.AddAccessRule($Rule)
        }
    }
    else {
        $Acl = New-Object Security.AccessControl.FileSecurity
        foreach ($Sid in $Allowed) {
            $Rule = New-Object Security.AccessControl.FileSystemAccessRule($Sid, [Security.AccessControl.FileSystemRights]::FullControl, [Security.AccessControl.AccessControlType]::Allow)
            [void]$Acl.AddAccessRule($Rule)
        }
    }
    $Acl.SetOwner($Current)
    $Acl.SetAccessRuleProtection($true, $false)
    Set-Acl -LiteralPath $Path -AclObject $Acl
}

function Assert-OwnerOnlyRuntimeAccess {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][bool]$Directory
    )
    $Acl = Get-Acl -LiteralPath $Path
    if (-not $Acl.AreAccessRulesProtected) { throw "AMS runtime path inherits access rules: $Path" }
    $Allowed = @((Get-RuntimeAllowedSids) | ForEach-Object { $_.Value })
    $Current = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $CurrentPresent = $false
    foreach ($Rule in @($Acl.GetAccessRules($true, $false, [Security.Principal.SecurityIdentifier]))) {
        if ($Rule.AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow -or $Allowed -notcontains $Rule.IdentityReference.Value) {
            throw "AMS runtime path grants access outside the current user/system/administrators boundary: $Path"
        }
        if ($Rule.IdentityReference.Value -eq $Current) { $CurrentPresent = $true }
    }
    if (-not $CurrentPresent) { throw "AMS runtime path does not grant the current user access: $Path" }
}

function Get-LocalHostId {
    $Value = (([Environment]::MachineName.ToLowerInvariant()) -replace '[^a-z0-9._-]', '')
    if (-not $Value -or $Value.Length -gt 128) { throw 'Unable to derive a safe local host identifier for the package/runtime lock.' }
    return $Value
}

function Protect-RuntimeTree {
    param([Parameter(Mandatory=$true)][string]$Path)
    Set-OwnerOnlyRuntimeAccess -Path $Path -Directory $true
    foreach ($Item in @(Get-ChildItem -LiteralPath $Path -Force -Recurse | Sort-Object { $_.FullName.Length })) {
        Set-OwnerOnlyRuntimeAccess -Path $Item.FullName -Directory ([bool]$Item.PSIsContainer)
    }
}

function Read-StrictRuntimeLines {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][Int64]$Maximum
    )
    $Item = Get-Item -LiteralPath $Path -Force
    if ($Item.PSIsContainer -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "AMS runtime record is not a safe regular file: $Path"
    }
    Assert-OwnerOnlyRuntimeAccess -Path $Path -Directory $false
    if ($Item.Length -le 0 -or $Item.Length -gt $Maximum) {
        throw "AMS runtime record size is invalid: $Path ($($Item.Length) bytes)"
    }
    $Fsutil = Get-Command fsutil.exe -ErrorAction SilentlyContinue
    if ($Fsutil) {
        $HardLinks = @(& $Fsutil.Source hardlink list $Path 2>$null)
        if ($LASTEXITCODE -eq 0 -and $HardLinks.Count -gt 1) { throw "AMS runtime record has multiple hard links: $Path" }
    }
    $Bytes = [IO.File]::ReadAllBytes($Path)
    if ($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) { throw "AMS runtime record has a UTF-8 BOM: $Path" }
    if ($Bytes[$Bytes.Length - 1] -ne 0x0A) { throw "AMS runtime record is missing final LF: $Path" }
    foreach ($Byte in $Bytes) {
        if ($Byte -eq 0x00 -or $Byte -eq 0x0D) { throw "AMS runtime record contains a forbidden NUL or CR byte: $Path" }
    }
    $Utf8 = New-Object Text.UTF8Encoding($false, $true)
    $Text = $Utf8.GetString($Bytes)
    foreach ($Character in $Text.ToCharArray()) {
        $Code = [int][char]$Character
        if (($Code -lt 32 -and $Code -ne 9 -and $Code -ne 10) -or ($Code -ge 127 -and $Code -le 159)) {
            throw "AMS runtime record contains a forbidden control character: $Path"
        }
    }
    $Lines = $Text.Split(@("`n"), [StringSplitOptions]::None)
    if ($Lines[$Lines.Count - 1] -ne '') { throw "AMS runtime record structure is invalid: $Path" }
    return @($Lines[0..($Lines.Count - 2)])
}

function Assert-ConvergenceRecord {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][ValidateSet('tracking','history')][string]$Kind,
        [Parameter(Mandatory=$true)][string]$Relative
    )
    $Lines = @(Read-StrictRuntimeLines -Path $Path -Maximum $MaxRuntimeRecordBytes)
    if ($Kind -eq 'tracking') {
        $Header = 'ams-convergence-tracking-v1'
        $Expected = @('campaign_id','root_objective_id','project_root','state','owner_id','owner_lease_expires_at','record_generation','created_at','updated_at','design_epoch_id','redesign_count','redesign_limit','epoch_correction_count','correction_limit','candidate_receipt','acceptance_boundary','candidate_surface','finding_fingerprints','last_resolution_action')
    }
    else {
        $Header = 'ams-convergence-history-v1'
        $Expected = @('campaign_id','root_objective_id','project_root','state','owner_id','owner_lease_expires_at','record_generation','created_at','updated_at','design_epoch_id','redesign_count','redesign_limit','epoch_correction_count','correction_limit','candidate_receipt','acceptance_boundary','candidate_surface','finding_fingerprints','last_resolution_action','terminal_disposition','terminal_receipt','closed_at')
    }
    if ($Lines.Count -ne ($Expected.Count + 1) -or $Lines[0] -cne $Header) { throw "AMS convergence record structure is invalid: $Relative" }
    $Fields = @{}
    foreach ($Line in $Lines[1..($Lines.Count - 1)]) {
        if ($Line.Length -gt 4096) { throw "AMS convergence record line is oversized: $Relative" }
        $Parts = $Line.Split([char]"`t")
        if ($Parts.Count -ne 2 -or $Parts[0] -notmatch '^[a-z_]+$' -or $Fields.ContainsKey($Parts[0])) { throw "AMS convergence record field is invalid: $Relative" }
        $Fields[$Parts[0]] = $Parts[1]
    }
    foreach ($Key in $Expected) { if (-not $Fields.ContainsKey($Key)) { throw "AMS convergence record is missing $Key`: $Relative" } }
    if ($Fields.Count -ne $Expected.Count) { throw "AMS convergence record contains an unexpected field: $Relative" }
    $Campaign = $Fields['campaign_id']
    if ($Campaign -notmatch '^cvg-[0-9a-f]{64}$') { throw "AMS convergence campaign ID is invalid: $Relative" }
    foreach ($IdentityField in @('root_objective_id','project_root','acceptance_boundary','candidate_surface')) {
        if (-not $Fields[$IdentityField]) { throw "AMS convergence identity is incomplete: $Relative" }
    }
    $IdentityText = "ams-convergence-campaign-v1`nproject_root`t$($Fields['project_root'])`nroot_objective_id`t$($Fields['root_objective_id'])`nacceptance_boundary`t$($Fields['acceptance_boundary'])`ncandidate_surface`t$($Fields['candidate_surface'])`n"
    $Hasher = [Security.Cryptography.SHA256]::Create()
    try { $ExpectedCampaign = 'cvg-' + (($Hasher.ComputeHash((New-Object Text.UTF8Encoding($false)).GetBytes($IdentityText)) | ForEach-Object { $_.ToString('x2') }) -join '') }
    finally { $Hasher.Dispose() }
    if ($Campaign -cne $ExpectedCampaign) { throw "AMS convergence campaign ID does not match its canonical identity: $Relative" }
    foreach ($Key in @('record_generation','redesign_count','redesign_limit','epoch_correction_count','correction_limit')) {
        if ($Fields[$Key] -notmatch '^[0-9]+$') { throw "AMS convergence counter is invalid: $Relative" }
    }
    $CorrectionLimit = [int]$Fields['correction_limit']; $RedesignLimit = [int]$Fields['redesign_limit']
    if ($CorrectionLimit -lt 2 -or $CorrectionLimit -gt 12 -or $RedesignLimit -lt 1 -or $RedesignLimit -gt 12) { throw "AMS convergence limits are invalid: $Relative" }
    $UtcPattern = '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    if ($Fields['created_at'] -notmatch $UtcPattern -or $Fields['updated_at'] -notmatch $UtcPattern) { throw "AMS convergence timestamps are invalid: $Relative" }
    if ($Fields['owner_lease_expires_at'] -cne 'none' -and $Fields['owner_lease_expires_at'] -notmatch $UtcPattern) { throw "AMS convergence lease timestamp is invalid: $Relative" }
    if ($Fields['finding_fingerprints'] -cne 'none' -and $Fields['finding_fingerprints'] -notmatch '^[0-9a-f]{64}(,[0-9a-f]{64}){0,7}$') { throw "AMS convergence fingerprints are invalid: $Relative" }
    $BaseName = [IO.Path]::GetFileName($Path)
    if ($Kind -eq 'tracking') {
        if ($Fields['state'] -notmatch '^(monitoring|convergence|intervention-required|terminal-pending-history)$') { throw "AMS convergence tracking state is invalid: $Relative" }
        if ($BaseName -cne "$Campaign.tracking.log") { throw "AMS convergence tracking filename does not match its campaign: $Relative" }
    }
    else {
        if ($Fields['state'] -cne 'terminal') { throw "AMS convergence history state is invalid: $Relative" }
        if ($Fields['terminal_disposition'] -notmatch '^(accept|accept-with-follow-up|blocked|failed|cancelled|user-disabled|user-override|superseded|stale)$') { throw "AMS convergence terminal disposition is invalid: $Relative" }
        if ($Fields['terminal_receipt'] -notmatch '^[0-9a-f]{64}$' -or $Fields['closed_at'] -notmatch $UtcPattern) { throw "AMS convergence terminal fields are invalid: $Relative" }
        if ($BaseName -cne "$Campaign.$($Fields['terminal_receipt']).record.log") { throw "AMS convergence history filename does not match its record: $Relative" }
    }
}

function Assert-SafeRuntimeState {
    param([Parameter(Mandatory=$true)][string]$Path)
    $Root = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if (-not $Root -or -not $Root.PSIsContainer -or ($Root.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "AMS runtime state is redirected or not a directory: $Path" }
    Assert-OwnerOnlyRuntimeAccess -Path $Path -Directory $true
    $RootPath = $Root.FullName.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    [Int64]$Total = 0; [int]$Count = 0
    foreach ($Item in @(Get-ChildItem -LiteralPath $Path -Force -Recurse -ErrorAction Stop)) {
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "AMS runtime state contains a redirected path: $($Item.FullName)" }
        $Relative = $Item.FullName.Substring($RootPath.Length + 1).Replace('\','/')
        if ($Item.PSIsContainer) {
            Assert-OwnerOnlyRuntimeAccess -Path $Item.FullName -Directory $true
            if ($Relative -cne 'convergence' -and $Relative -cne 'convergence/history') { throw "AMS runtime state contains an unexpected directory: $Relative" }
            continue
        }
        if ($Relative -match '^convergence/cvg-[0-9a-f]{64}\.tracking\.log$') { Assert-ConvergenceRecord -Path $Item.FullName -Kind tracking -Relative $Relative }
        elseif ($Relative -match '^convergence/history/cvg-[0-9a-f]{64}\.[0-9a-f]{64}\.record\.log$') { Assert-ConvergenceRecord -Path $Item.FullName -Kind history -Relative $Relative }
        else { throw "AMS runtime state contains an unexpected file: $Relative" }
        $Total += $Item.Length; $Count++
        if ($Total -gt $MaxRuntimeBytes -or $Count -gt $MaxRuntimeFiles) { throw "AMS runtime state exceeds the preservation bound." }
    }
}

function Get-RuntimeStateSnapshot {
    param([Parameter(Mandatory=$true)][string]$Path)
    Assert-SafeRuntimeState -Path $Path
    $Root = (Get-Item -LiteralPath $Path -Force).FullName.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    return @(Get-ChildItem -LiteralPath $Path -Force -Recurse -File | ForEach-Object {
        $Relative = $_.FullName.Substring($Root.Length + 1).Replace('\','/')
        "{0}`t{1}`t{2}" -f $Relative, $_.Length, (Get-Sha256 -Path $_.FullName)
    } | Sort-Object -CaseSensitive)
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
    foreach ($Character in $Text.ToCharArray()) {
        $Code = [int][char]$Character
        if (($Code -lt 32 -and $Code -ne 9 -and $Code -ne 10) -or ($Code -ge 127 -and $Code -le 159)) {
            throw "Install manifest contains a forbidden control character: $Path"
        }
    }
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

$LockPath = Join-Path $SkillHome ".$SkillName.runtime.lock"
$LockOwner = "installer-$PID-$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ'))"
$LockHost = Get-LocalHostId
$LockQuarantine = $null

function Read-SharedRuntimeLockOwner {
    param([Parameter(Mandatory=$true)][string]$Directory)
    $Item = Get-Item -LiteralPath $Directory -Force -ErrorAction SilentlyContinue
    if (-not $Item -or -not $Item.PSIsContainer -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "Package/runtime lock path is redirected or not a directory: $Directory" }
    Assert-OwnerOnlyRuntimeAccess -Path $Directory -Directory $true
    $OwnerPath = Join-Path $Directory 'owner.log'
    $Lines = @(Read-StrictRuntimeLines -Path $OwnerPath -Maximum 4096)
    $Expected = @('owner_id','purpose','campaign_id','host_id','pid','acquired_epoch','lease_expires_epoch')
    if ($Lines.Count -ne 8 -or $Lines[0] -cne 'ams-runtime-lock-v1') { throw "Package/runtime lock owner record is malformed: $OwnerPath" }
    $Fields = @{}
    foreach ($Line in $Lines[1..7]) {
        $Parts = $Line.Split([char]"`t")
        if ($Parts.Count -ne 2 -or $Fields.ContainsKey($Parts[0])) { throw "Package/runtime lock owner record is malformed: $OwnerPath" }
        $Fields[$Parts[0]] = $Parts[1]
    }
    foreach ($Key in $Expected) { if (-not $Fields.ContainsKey($Key)) { throw "Package/runtime lock owner record is missing $Key" } }
    if ($Fields['owner_id'] -notmatch '^[A-Za-z0-9._-]{1,128}$') { throw 'Package/runtime lock owner ID is invalid.' }
    if ($Fields['purpose'] -notmatch '^(installer|convergence|startup-recovery|runtime-export|runtime-import|package-maintenance)$') { throw 'Package/runtime lock purpose is invalid.' }
    if ($Fields['campaign_id'] -cne 'none' -and $Fields['campaign_id'] -notmatch '^cvg-[0-9a-f]{64}$') { throw 'Package/runtime lock campaign ID is invalid.' }
    if ($Fields['host_id'] -notmatch '^[a-z0-9._-]{1,128}$') { throw 'Package/runtime lock host ID is invalid.' }
    if ($Fields['pid'] -cne 'none' -and $Fields['pid'] -notmatch '^[1-9][0-9]*$') { throw 'Package/runtime lock PID is invalid.' }
    if ($Fields['acquired_epoch'] -notmatch '^[0-9]+$' -or $Fields['lease_expires_epoch'] -notmatch '^[0-9]+$' -or [Int64]$Fields['lease_expires_epoch'] -lt [Int64]$Fields['acquired_epoch']) { throw 'Package/runtime lock lease is invalid.' }
    return [PSCustomObject]@{ Fields=$Fields; Bytes=[Convert]::ToBase64String([IO.File]::ReadAllBytes($OwnerPath)); Path=$OwnerPath }
}

function Get-OwnerlessLockSnapshot {
    param([Parameter(Mandatory=$true)][string]$Directory)
    $Rows = New-Object 'System.Collections.Generic.List[string]'
    $Items = @(Get-ChildItem -LiteralPath $Directory -Force | Sort-Object -Property Name -CaseSensitive)
    if ($Items.Count -gt 1) { throw 'Ownerless package/runtime lock contains more than one staging owner file.' }
    foreach ($Item in $Items) {
        if ($Item.PSIsContainer -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $Item.Name -notmatch '^\.owner-[A-Za-z0-9._-]+$') {
            throw "Ownerless package/runtime lock contains an unexpected entry: $($Item.FullName)"
        }
        if ($Item.Length -gt 4096) { throw "Ownerless package/runtime lock staging file is oversized: $($Item.FullName)" }
        Assert-OwnerOnlyRuntimeAccess -Path $Item.FullName -Directory $false
        $Rows.Add(("{0}`t{1}`t{2}" -f $Item.Name, $Item.Length, (Get-Sha256 -Path $Item.FullName)))
    }
    return ($Rows.ToArray() -join "`n")
}

function Publish-SharedRuntimeLock {
    New-Item -ItemType Directory -Path $LockPath -ErrorAction Stop | Out-Null
    Set-OwnerOnlyRuntimeAccess -Path $LockPath -Directory $true
    $NowEpoch = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    $OwnerText = @(
        'ams-runtime-lock-v1',
        "owner_id`t$LockOwner",
        "purpose`tinstaller",
        "campaign_id`tnone",
        "host_id`t$LockHost",
        "pid`t$PID",
        "acquired_epoch`t$NowEpoch",
        "lease_expires_epoch`t$($NowEpoch + 21600)"
    ) -join "`n"
    $OwnerTemp = Join-Path $LockPath ".owner-$PID-$([Guid]::NewGuid().ToString('N'))"
    [IO.File]::WriteAllText($OwnerTemp, $OwnerText + "`n", (New-Object Text.UTF8Encoding($false)))
    Set-OwnerOnlyRuntimeAccess -Path $OwnerTemp -Directory $false
    Move-Item -LiteralPath $OwnerTemp -Destination (Join-Path $LockPath 'owner.log')
    Set-OwnerOnlyRuntimeAccess -Path (Join-Path $LockPath 'owner.log') -Directory $false
    $Published = Read-SharedRuntimeLockOwner -Directory $LockPath
    if ($Published.Fields['owner_id'] -cne $LockOwner) { throw 'Package/runtime lock owner verification failed.' }
}

function Acquire-SharedRuntimeLock {
    foreach ($Attempt in 1..3) {
        try { Publish-SharedRuntimeLock; return }
        catch {
            if (-not (Test-Path -LiteralPath $LockPath)) { if ($Attempt -eq 3) { throw }; continue }
        }
        $OwnerPath = Join-Path $LockPath 'owner.log'
        if (-not (Test-Path -LiteralPath $OwnerPath -PathType Leaf)) {
            $LockItem = Get-Item -LiteralPath $LockPath -Force
            $AgeSeconds = ([DateTime]::UtcNow - $LockItem.LastWriteTimeUtc).TotalSeconds
            if ($AgeSeconds -le 30) { throw "Package/runtime lock initialization is still within its grace period: $LockPath" }
            $Before = Get-OwnerlessLockSnapshot -Directory $LockPath
            Start-Sleep -Seconds 1
            if (Test-Path -LiteralPath $OwnerPath -PathType Leaf) { continue }
            $After = Get-OwnerlessLockSnapshot -Directory $LockPath
            if ($After -cne $Before) { continue }
            $NowEpoch = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
            $Quarantine = "$LockPath.stale.$NowEpoch.$LockOwner"
            if (Test-Path -LiteralPath $Quarantine) { throw "Stale-lock quarantine path already exists: $Quarantine" }
            try { Move-Item -LiteralPath $LockPath -Destination $Quarantine -ErrorAction Stop }
            catch { continue }
            if ((Get-OwnerlessLockSnapshot -Directory $Quarantine) -cne $Before) {
                if (-not (Test-Path -LiteralPath $LockPath) -and (Test-Path -LiteralPath $Quarantine)) { Move-Item -LiteralPath $Quarantine -Destination $LockPath -ErrorAction SilentlyContinue }
                throw 'Ownerless package/runtime lock changed during quarantine; takeover refused.'
            }
            try { Publish-SharedRuntimeLock; $script:LockQuarantine=$Quarantine; Remove-Item -LiteralPath $Quarantine -Recurse -Force; $script:LockQuarantine=$null; return }
            catch {
                if (-not (Test-Path -LiteralPath $LockPath) -and (Test-Path -LiteralPath $Quarantine)) { Move-Item -LiteralPath $Quarantine -Destination $LockPath -ErrorAction SilentlyContinue }
                throw
            }
        }
        $Existing = Read-SharedRuntimeLockOwner -Directory $LockPath
        $NowEpoch = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        if ([Int64]$Existing.Fields['lease_expires_epoch'] -gt $NowEpoch) {
            throw "Another AMS package/runtime writer holds the lock: owner=$($Existing.Fields['owner_id']), purpose=$($Existing.Fields['purpose']), expires=$($Existing.Fields['lease_expires_epoch'])"
        }
        if ($Existing.Fields['host_id'] -cne $LockHost) { throw "Expired package/runtime lock belongs to another host; takeover is ambiguous: $($Existing.Fields['host_id'])" }
        if ($Existing.Fields['pid'] -ceq 'none') { throw 'Expired package/runtime lock has no process identity; takeover is ambiguous.' }
        if (Get-Process -Id ([int]$Existing.Fields['pid']) -ErrorAction SilentlyContinue) { throw "Expired package/runtime lock owner process is still live: $($Existing.Fields['pid'])" }
        if ([Convert]::ToBase64String([IO.File]::ReadAllBytes($Existing.Path)) -cne $Existing.Bytes) { continue }
        $Quarantine = "$LockPath.stale.$NowEpoch.$LockOwner"
        if (Test-Path -LiteralPath $Quarantine) { throw "Stale-lock quarantine path already exists: $Quarantine" }
        try { Move-Item -LiteralPath $LockPath -Destination $Quarantine -ErrorAction Stop }
        catch { continue }
        $QuarantinedOwner = Join-Path $Quarantine 'owner.log'
        if ([Convert]::ToBase64String([IO.File]::ReadAllBytes($QuarantinedOwner)) -cne $Existing.Bytes) {
            if (-not (Test-Path -LiteralPath $LockPath) -and (Test-Path -LiteralPath $Quarantine)) { Move-Item -LiteralPath $Quarantine -Destination $LockPath -ErrorAction SilentlyContinue }
            throw 'Stale package/runtime lock owner changed during quarantine; takeover refused.'
        }
        try { Publish-SharedRuntimeLock; $script:LockQuarantine=$Quarantine; Remove-Item -LiteralPath $Quarantine -Recurse -Force; $script:LockQuarantine=$null; return }
        catch {
            if (-not (Test-Path -LiteralPath $LockPath) -and (Test-Path -LiteralPath $Quarantine)) { Move-Item -LiteralPath $Quarantine -Destination $LockPath -ErrorAction SilentlyContinue }
            throw
        }
    }
    throw "Package/runtime lock changed repeatedly; retry after inspecting $LockPath."
}

Acquire-SharedRuntimeLock

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
$RuntimeStatePresent = $false
$RuntimeSnapshotBefore = @()

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
    $ExistingRuntime = Join-Path $Destination ".runtime"
    if (Test-Path -LiteralPath $ExistingRuntime) {
        $RuntimeSnapshotBefore = @(Get-RuntimeStateSnapshot -Path $ExistingRuntime)
        $RuntimeStatePresent = $true
    }
    if ($Existing) {
        if ($Existing.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Refusing to replace a redirected existing skill path: $Destination" }
        if (-not $Existing.PSIsContainer) { throw "Refusing to replace a non-directory existing skill path: $Destination" }
        if (Test-Path -LiteralPath $BackupPath) { throw "Unexpected backup collision: $BackupPath" }
        Move-Item -LiteralPath $Destination -Destination $BackupPath
        $ExistingMoved = $true
    }

    Move-Item -LiteralPath $Candidate -Destination $Destination
    $CandidateInstalled = $true

    if ($RuntimeStatePresent) {
        $SavedRuntime = Join-Path $BackupPath ".runtime"
        $InstalledRuntime = Join-Path $Destination ".runtime"
        if (-not (Test-Path -LiteralPath $SavedRuntime -PathType Container)) { throw "Preserved AMS runtime state disappeared during replacement." }
        if (Test-Path -LiteralPath $InstalledRuntime) { throw "Candidate unexpectedly contains package-local runtime state." }
        Copy-Item -LiteralPath $SavedRuntime -Destination $InstalledRuntime -Recurse
        Protect-RuntimeTree -Path $InstalledRuntime
        $RuntimeSnapshotAfter = @(Get-RuntimeStateSnapshot -Path $InstalledRuntime)
        if ($RuntimeSnapshotBefore.Count -ne $RuntimeSnapshotAfter.Count) { throw "AMS runtime state changed during preservation; retry from a stable record boundary." }
        for ($RuntimeIndex = 0; $RuntimeIndex -lt $RuntimeSnapshotBefore.Count; $RuntimeIndex++) {
            if ($RuntimeSnapshotBefore[$RuntimeIndex] -cne $RuntimeSnapshotAfter[$RuntimeIndex]) { throw "AMS runtime state changed during preservation; retry from a stable record boundary." }
        }
    }

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
    Write-Host "Installation complete."
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
    $OwnerPath = Join-Path $LockPath 'owner.log'
    if (Test-Path -LiteralPath $OwnerPath -PathType Leaf) {
        $OwnerBytes = [IO.File]::ReadAllText($OwnerPath)
        if ($OwnerBytes -match "(?m)^owner_id`t$([regex]::Escape($LockOwner))$") { Remove-Item -LiteralPath $LockPath -Recurse -Force -ErrorAction SilentlyContinue }
    }
    if ($LockQuarantine -and (Test-Path -LiteralPath $LockQuarantine)) { Remove-Item -LiteralPath $LockQuarantine -Recurse -Force -ErrorAction SilentlyContinue }
}
