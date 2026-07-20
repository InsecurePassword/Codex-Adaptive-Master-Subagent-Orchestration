# Adaptive Master-Subagent Orchestration deployment
# Version 4.0.0
# Windows PowerShell 5.1; no Python or external modules required.
#
# Public install command after repository publication:
# powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "iex (irm 'https://raw.githubusercontent.com/InsecurePassword/adaptive-master-subagent-orchestration/main/deploy.ps1')"
# Set AMS_ACTION to Repair or Uninstall before the same IEX command for those operations.

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [ValidateSet("Install", "Repair", "Uninstall")]
    [string]$Action = "Install",

    [string]$HomeDirectory = $HOME,

    [ValidateSet("auto", "minimal", "moderate", "heavy", "extreme")]
    [string]$Intensity = "auto",

    [object]$SparkEfforts = "low,medium,high",
    [switch]$ExcludeSpark,
    [switch]$Force,
    [string]$ArchivePath,
    [string]$SourceDirectory,

    [Alias("Ref")]
    [string]$RepositoryRef
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

$Version = "4.0.0"
$Repository = "InsecurePassword/adaptive-master-subagent-orchestration"
$ManagedMarker = "# managed-by: adaptive-master-subagent-orchestration"
$SkillName = "ams-orchestration"
$PayloadDirectory = "adaptive-master-subagent-orchestration-option-c-installer-required"
$ValidIntensities = @("auto", "minimal", "moderate", "heavy", "extreme")
$ValidSparkEfforts = @("low", "medium", "high")
$Utf8NoBom = New-Object System.Text.UTF8Encoding -ArgumentList $false
$TempRoot = $null
$LockStream = $null
$LockPath = $null

function Write-Heading([string]$Text) {
    Write-Host ""
    Write-Host $Text -ForegroundColor Cyan
    Write-Host ("=" * $Text.Length) -ForegroundColor DarkCyan
}

function Get-FullPath([string]$Path) {
    return [System.IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($Path))
}

function Read-Utf8([string]$Path) {
    return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

function Write-Utf8([string]$Path, [string]$Text) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force | Out-Null
    $Temporary = "$Path.$([Guid]::NewGuid().ToString('N')).tmp"
    try {
        [System.IO.File]::WriteAllText($Temporary, $Text, $Utf8NoBom)
        Move-Item -LiteralPath $Temporary -Destination $Path -Force
    }
    finally {
        Remove-Item -LiteralPath $Temporary -Force -ErrorAction SilentlyContinue
    }
}

function Test-ManagedFile([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    $Reader = New-Object System.IO.StreamReader($Path, [System.Text.Encoding]::UTF8, $true)
    try { return ($Reader.ReadLine() -ceq $ManagedMarker) }
    finally { $Reader.Dispose() }
}

function Test-ManagedSkill([string]$Path) {
    $Marker = Join-Path $Path ".ams-managed"
    return ((Test-Path -LiteralPath $Marker -PathType Leaf) -and (Read-Utf8 $Marker).StartsWith("adaptive-master-subagent-orchestration`n"))
}

function Get-Hash([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Convert-SparkEfforts([object]$Value) {
    $Result = @()
    foreach ($Entry in @($Value)) {
        if ($null -eq $Entry) { continue }
        foreach ($Part in ([string]$Entry).Split(",")) {
            $Effort = $Part.Trim().ToLowerInvariant()
            if (-not $Effort) { continue }
            if ($ValidSparkEfforts -notcontains $Effort) { throw "Unsupported Spark effort: $Part" }
            if ($Result -notcontains $Effort) { $Result += $Effort }
        }
    }
    return $Result
}

function Enter-Lock([string]$Path) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force | Out-Null
    if (Test-Path -LiteralPath $Path) {
        $Age = (Get-Date) - (Get-Item -LiteralPath $Path).LastWriteTime
        if ($Age.TotalHours -le 2) { throw "Another AMS deployment appears active: $Path" }
        Remove-Item -LiteralPath $Path -Force
    }
    $script:LockStream = New-Object System.IO.FileStream($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    $Bytes = $Utf8NoBom.GetBytes("pid=$PID`n")
    $script:LockStream.Write($Bytes, 0, $Bytes.Length)
    $script:LockStream.Flush()
    $script:LockPath = $Path
}

function Exit-Lock {
    if ($null -ne $script:LockStream) { $script:LockStream.Dispose(); $script:LockStream = $null }
    if ($script:LockPath) { Remove-Item -LiteralPath $script:LockPath -Force -ErrorAction SilentlyContinue; $script:LockPath = $null }
}

function Download-Source([string]$Ref, [string]$RequestedArchive) {
    $script:TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("ams-deploy-" + [Guid]::NewGuid().ToString("N"))
    $Archive = Join-Path $script:TempRoot "repository.zip"
    $Extracted = Join-Path $script:TempRoot "extracted"
    New-Item -ItemType Directory -Path $script:TempRoot -Force | Out-Null

    if ($RequestedArchive) {
        Copy-Item -LiteralPath (Get-FullPath $RequestedArchive) -Destination $Archive -Force
    }
    else {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        $Headers = @{}
        $Url = "https://github.com/$Repository/archive/refs/heads/$Ref.zip"
        if ($env:GITHUB_TOKEN) {
            $Url = "https://api.github.com/repos/$Repository/zipball/$Ref"
            $Headers = @{
                Authorization = "Bearer $($env:GITHUB_TOKEN)"
                Accept = "application/vnd.github+json"
                "X-GitHub-Api-Version" = "2022-11-28"
                "User-Agent" = "ams-deploy"
            }
        }
        $Request = @{ Uri = $Url; OutFile = $Archive; UseBasicParsing = $true; TimeoutSec = 120 }
        if ($Headers.Count) { $Request.Headers = $Headers }
        Invoke-WebRequest @Request
    }

    Expand-Archive -LiteralPath $Archive -DestinationPath $Extracted -Force
    $Candidates = @(Get-ChildItem -LiteralPath $Extracted -Directory -Recurse | Where-Object {
        (Test-Path (Join-Path $_.FullName "VERSION") -PathType Leaf) -and
        (Test-Path (Join-Path $_.FullName "MANIFEST.sha256") -PathType Leaf) -and
        (Test-Path (Join-Path $_.FullName ($PayloadDirectory + "\skills\ams-orchestration\SKILL.md")) -PathType Leaf)
    })
    if ($Candidates.Count -ne 1) { throw "Expected one AMS source root; found $($Candidates.Count)." }
    return $Candidates[0].FullName
}

function Get-PayloadFiles([string]$Root) {
    $Files = @(
        Get-Item (Join-Path $Root "VERSION"),
        Get-Item (Join-Path $Root "deploy.ps1")
    )
    foreach ($Directory in @("assets", "skills", "config")) {
        $Files += Get-ChildItem -LiteralPath (Join-Path $Root ($PayloadDirectory + "\" + $Directory)) -File -Recurse
    }
    return @($Files | Sort-Object FullName)
}

function Validate-Source([string]$Root) {
    if ((Read-Utf8 (Join-Path $Root "VERSION")).Trim() -ne $Version) { throw "Source version mismatch." }

    $Expected = @{}
    foreach ($Line in [System.IO.File]::ReadAllLines((Join-Path $Root "MANIFEST.sha256"))) {
        if (-not $Line.Trim()) { continue }
        if ($Line -notmatch '^([0-9a-fA-F]{64})  (.+)$') { throw "Malformed manifest line: $Line" }
        $Expected[$Matches[2].Replace("\", "/")] = $Matches[1].ToLowerInvariant()
    }
    $Actual = @{}
    foreach ($File in Get-PayloadFiles $Root) {
        $Relative = $File.FullName.Substring($Root.Length).TrimStart([char[]]@([char]'\', [char]'/')).Replace("\", "/")
        $Actual[$Relative] = Get-Hash $File.FullName
    }
    if ($Expected.Count -ne $Actual.Count) { throw "Manifest file count mismatch." }
    foreach ($Path in $Actual.Keys) {
        if (-not $Expected.ContainsKey($Path) -or $Expected[$Path] -ne $Actual[$Path]) { throw "Manifest verification failed: $Path" }
    }

    $Policy = Read-Utf8 (Join-Path $Root ($PayloadDirectory + "\skills\ams-orchestration\agents\openai.yaml"))
    if ($Policy -notmatch '(?m)^\s*allow_implicit_invocation:\s*true\s*$' -or $Policy -match 'allow_implicit_invocation:\s*false') {
        throw "Implicit invocation is not enabled."
    }
    $Skill = Read-Utf8 (Join-Path $Root ($PayloadDirectory + "\skills\ams-orchestration\SKILL.md"))
    if ($Skill -notmatch 'intensity = "auto"') { throw "Auto is not the default intensity." }
    if ((Get-ChildItem (Join-Path $Root ($PayloadDirectory + "\assets\agent-profiles\ams_*.toml")) -File).Count -ne 18) { throw "Expected 18 profile definitions." }
}

function Backup-Item([string]$Path, [string]$BackupRoot) {
    if (-not (Test-Path -LiteralPath $Path)) { return }
    New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
    $Name = ([System.IO.Path]::GetFileName($Path) + "." + (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss") + ".bak")
    $Destination = Join-Path $BackupRoot $Name
    $Index = 2
    while (Test-Path $Destination) { $Destination = Join-Path $BackupRoot ($Name + ".$Index"); $Index++ }
    Copy-Item -LiteralPath $Path -Destination $Destination -Recurse -Force
}

function Get-DesiredProfiles([string[]]$Spark, [bool]$NoSpark) {
    $Names = @()
    foreach ($Family in @("sol", "terra", "luna")) {
        foreach ($Effort in @("low", "medium", "high", "xhigh", "max")) { $Names += "ams_${Family}_${Effort}" }
    }
    if (-not $NoSpark) { foreach ($Effort in $Spark) { $Names += "ams_spark_${Effort}" } }
    return $Names
}

function Get-IntensityValue([string]$Text) {
    if ($Text -match '(?m)^\s*intensity\s*=\s*"(auto|minimal|moderate|heavy|extreme)"') { return $Matches[1] }
    return $null
}

function Ensure-MaxDepth([string]$Path) {
    $Text = if (Test-Path $Path -PathType Leaf) { Read-Utf8 $Path } else { "" }
    if ($Text -match '(?m)^\s*max_depth\s*=\s*([0-9]+)') {
        if ([int]$Matches[1] -ne 1) { throw "Existing agents.max_depth is $($Matches[1]); AMS requires 1." }
        return
    }
    $AgentSections = [regex]::Matches($Text, '(?m)^\s*\[agents\]\s*$')
    if ($AgentSections.Count -gt 1) { throw "Codex configuration contains multiple [agents] sections." }
    if ($AgentSections.Count -eq 1) {
        $Text = [regex]::Replace($Text, '(?m)^(\s*\[agents\]\s*)$', "`$1`nmax_depth = 1 $ManagedMarker")
    }
    else {
        $Text = $Text.TrimEnd() + "`n`n[agents]`nmax_depth = 1 $ManagedMarker`n"
    }
    Write-Utf8 $Path $Text
}

function Remove-ManagedMaxDepth([string]$Path) {
    if (-not (Test-Path $Path -PathType Leaf)) { return }
    $Text = Read-Utf8 $Path
    $Text = [regex]::Replace($Text, '(?m)^\s*max_depth\s*=\s*1\s*#\s*managed-by:\s*adaptive-master-subagent-orchestration\s*\r?\n?', '')
    $Text = [regex]::Replace($Text, '(?ms)^\s*\[agents\]\s*\r?\n(?=\s*(?:\[[^\]]+\]|\z))', '')
    if ($Text.Trim()) { Write-Utf8 $Path ($Text.TrimEnd() + "`n") } else { Remove-Item $Path -Force }
}

function Install-Ams([string]$SourceRoot, [string]$Home, [string]$CodexHome, [string[]]$Spark, [bool]$NoSpark, [bool]$IntensitySpecified) {
    Validate-Source $SourceRoot

    $PayloadRoot = Join-Path $SourceRoot $PayloadDirectory
    $SkillSource = Join-Path $PayloadRoot "skills\ams-orchestration"
    $ProfileSource = Join-Path $PayloadRoot "assets\agent-profiles"
    $SkillTarget = Join-Path $Home ".agents\skills\ams-orchestration"
    $AgentTarget = Join-Path $CodexHome "agents"
    $IntensityTarget = Join-Path $CodexHome "ams-orchestration.toml"
    $ConfigTarget = Join-Path $CodexHome "config.toml"
    $BackupRoot = Join-Path $Home ".agents\ams-orchestration\backups"
    $Desired = @(Get-DesiredProfiles $Spark $NoSpark)

    if ((Test-Path $SkillTarget) -and -not (Test-ManagedSkill $SkillTarget)) { throw "Refusing to replace unowned skill: $SkillTarget" }
    foreach ($Source in Get-ChildItem (Join-Path $ProfileSource "ams_*.toml") -File) {
        $Target = Join-Path $AgentTarget $Source.Name
        if (($Desired -contains $Source.BaseName) -and (Test-Path $Target) -and -not (Test-ManagedFile $Target)) {
            throw "Refusing to replace unowned profile: $Target"
        }
    }
    if ((Test-Path $IntensityTarget) -and -not (Test-ManagedFile $IntensityTarget) -and $IntensitySpecified) {
        throw "Refusing to modify unowned intensity configuration: $IntensityTarget"
    }

    $ExistingIntensity = if (Test-Path $IntensityTarget -PathType Leaf) { Get-IntensityValue (Read-Utf8 $IntensityTarget) } else { $null }
    $ResolvedIntensity = if ($IntensitySpecified) { $Intensity } elseif ($ExistingIntensity) { $ExistingIntensity } else { "auto" }

    Write-Host "Skill: $SkillTarget"
    Write-Host "Profiles: $($Desired.Count)"
    Write-Host "Intensity: $ResolvedIntensity"
    if ($WhatIfPreference) { Write-Host "WhatIf: no changes made."; return }

    New-Item -ItemType Directory -Path (Split-Path $SkillTarget -Parent), $AgentTarget, $CodexHome -Force | Out-Null
    Backup-Item $SkillTarget $BackupRoot
    if (Test-Path $SkillTarget) { Remove-Item $SkillTarget -Recurse -Force }
    Copy-Item $SkillSource -Destination $SkillTarget -Recurse -Force
    [System.IO.File]::WriteAllText((Join-Path $SkillTarget ".ams-managed"), "adaptive-master-subagent-orchestration`nversion=$Version`n", $Utf8NoBom)

    foreach ($Source in Get-ChildItem (Join-Path $ProfileSource "ams_*.toml") -File) {
        $Name = $Source.BaseName
        $Target = Join-Path $AgentTarget $Source.Name
        if ($Desired -contains $Name) {
            Backup-Item $Target $BackupRoot
            Copy-Item $Source.FullName -Destination $Target -Force
        }
        elseif ((Test-Path $Target) -and (Test-ManagedFile $Target)) {
            Backup-Item $Target $BackupRoot
            Remove-Item $Target -Force
        }
    }

    if (-not (Test-Path $IntensityTarget) -or (Test-ManagedFile $IntensityTarget)) {
        Write-Utf8 $IntensityTarget "$ManagedMarker`nschema_version = 1`nintensity = `"$ResolvedIntensity`"`n"
    }
    Ensure-MaxDepth $ConfigTarget

    if (-not (Test-ManagedSkill $SkillTarget)) { throw "Skill verification failed." }
    if ((Read-Utf8 (Join-Path $SkillTarget "agents\openai.yaml")) -notmatch 'allow_implicit_invocation:\s*true') { throw "Implicit invocation verification failed." }
    foreach ($Name in $Desired) {
        if (-not (Test-ManagedFile (Join-Path $AgentTarget ($Name + ".toml")))) { throw "Profile verification failed: $Name" }
    }
    Write-Host "$Action completed successfully." -ForegroundColor Green
}

function Uninstall-Ams([string]$Home, [string]$CodexHome) {
    if (-not $Force -and $env:AMS_UNINSTALL_FORCE -ne "1") {
        Write-Warning "This removes package-managed AMS files and configuration."
        if ((Read-Host "Type REMOVE to continue") -cne "REMOVE") { Write-Host "Uninstall cancelled."; return }
    }
    $SkillTarget = Join-Path $Home ".agents\skills\ams-orchestration"
    $AgentTarget = Join-Path $CodexHome "agents"
    $IntensityTarget = Join-Path $CodexHome "ams-orchestration.toml"
    $ConfigTarget = Join-Path $CodexHome "config.toml"
    $StateRoot = Join-Path $Home ".agents\ams-orchestration"

    if ($WhatIfPreference) { Write-Host "WhatIf: managed AMS files would be removed."; return }
    if ((Test-Path $SkillTarget) -and (Test-ManagedSkill $SkillTarget)) { Remove-Item $SkillTarget -Recurse -Force }
    if (Test-Path $AgentTarget -PathType Container) {
        foreach ($Profile in Get-ChildItem (Join-Path $AgentTarget "ams_*.toml") -File -ErrorAction SilentlyContinue) {
            if (Test-ManagedFile $Profile.FullName) { Remove-Item $Profile.FullName -Force }
        }
    }
    if ((Test-Path $IntensityTarget) -and (Test-ManagedFile $IntensityTarget)) { Remove-Item $IntensityTarget -Force }
    Remove-ManagedMaxDepth $ConfigTarget
    if (Test-Path $StateRoot) { Remove-Item $StateRoot -Recurse -Force }
    Write-Host "Uninstall completed successfully." -ForegroundColor Green
}

try {
    if (-not $PSBoundParameters.ContainsKey("Action") -and $env:AMS_ACTION) {
        switch ($env:AMS_ACTION.Trim().ToLowerInvariant()) {
            "install" { $Action = "Install" }
            "repair" { $Action = "Repair" }
            "uninstall" { $Action = "Uninstall" }
            default { throw "Unsupported AMS_ACTION: $($env:AMS_ACTION)" }
        }
    }
    $IntensitySpecified = $PSBoundParameters.ContainsKey("Intensity")
    if (-not $IntensitySpecified -and $env:AMS_INTENSITY) {
        $Intensity = $env:AMS_INTENSITY.Trim().ToLowerInvariant()
        if ($ValidIntensities -notcontains $Intensity) { throw "Unsupported AMS_INTENSITY: $Intensity" }
        $IntensitySpecified = $true
    }
    if (-not $PSBoundParameters.ContainsKey("SparkEfforts") -and $env:AMS_SPARK_EFFORTS) { $SparkEfforts = $env:AMS_SPARK_EFFORTS }
    if (-not $PSBoundParameters.ContainsKey("HomeDirectory") -and $env:AMS_HOME) { $HomeDirectory = $env:AMS_HOME }

    $HomeDirectory = Get-FullPath $HomeDirectory
    $CodexHome = if ($env:CODEX_HOME) { Get-FullPath $env:CODEX_HOME } else { Join-Path $HomeDirectory ".codex" }
    $Spark = @(Convert-SparkEfforts $SparkEfforts)
    $NoSpark = $ExcludeSpark -or $env:AMS_EXCLUDE_SPARK -eq "1"
    if (-not $NoSpark -and $Spark.Count -eq 0) { throw "SparkEfforts cannot be empty unless Spark is excluded." }

    if (-not $WhatIfPreference) {
        $LockPath = Join-Path $HomeDirectory ".agents\.ams-orchestration-deploy.lock"
        Enter-Lock $LockPath
    }
    try {
        if ($Action -eq "Uninstall") {
            Write-Heading "Uninstalling Adaptive Master-Subagent Orchestration"
            Uninstall-Ams $HomeDirectory $CodexHome
        }
        else {
            if ($SourceDirectory) {
                $SourceRoot = Get-FullPath $SourceDirectory
            }
            else {
                $Ref = if ($RepositoryRef) { $RepositoryRef.Trim() } elseif ($env:AMS_REF) { $env:AMS_REF.Trim() } else { "main" }
                if ($Ref -notmatch '^[A-Za-z0-9._/-]+$' -or $Ref.Contains("..")) { throw "Unsupported repository ref: $Ref" }
                $SourceRoot = Download-Source $Ref $ArchivePath
            }
            Write-Heading ("{0}ing Adaptive Master-Subagent Orchestration" -f $Action)
            Install-Ams $SourceRoot $HomeDirectory $CodexHome $Spark $NoSpark $IntensitySpecified
        }
    }
    finally { Exit-Lock }
}
catch {
    Exit-Lock
    Write-Error $_.Exception.Message
    exit 1
}
finally {
    if ($TempRoot -and (Test-Path $TempRoot)) { Remove-Item $TempRoot -Recurse -Force -ErrorAction SilentlyContinue }
}
