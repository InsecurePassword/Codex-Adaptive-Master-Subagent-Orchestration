#requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$ThreadId,
    [string]$SessionsDir
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
$MaxRolloutBytes = 64MB
$MaxLineChars = 4MB
$MaxDirectories = 10000
$MaxEntries = 200000
$MaxDepth = 16

function Get-OptionalProperty {
    param([object]$Object, [string]$Name)
    if ($null -eq $Object) { return $null }
    $Property = $Object.PSObject.Properties[$Name]
    if ($null -eq $Property -or $Property.Value -isnot [string]) { return $null }
    return [string]$Property.Value
}

function Get-UniqueValue {
    param([object[]]$Values, [string]$Label, [switch]$AllowNull)
    if ($Values.Count -eq 0) { throw "missing $Label" }
    $Unique = New-Object 'System.Collections.Generic.List[object]'
    foreach ($Value in $Values) {
        if (-not $AllowNull -and ($null -eq $Value -or $Value -eq "")) { throw "missing $Label" }
        $Found = $false
        foreach ($Existing in $Unique) {
            if (($null -eq $Existing -and $null -eq $Value) -or
                ($null -ne $Existing -and $null -ne $Value -and ([string]$Existing -ceq [string]$Value))) {
                $Found = $true; break
            }
        }
        if (-not $Found) { $Unique.Add($Value) }
    }
    if ($Unique.Count -ne 1) { throw "conflicting $Label" }
    $Result = $Unique[0]
    if (-not $AllowNull -and ($null -eq $Result -or $Result -eq "")) { throw "missing $Label" }
    return $Result
}

function Find-ExactRollouts {
    param([string]$Root, [string]$Suffix)
    $Matches = New-Object 'System.Collections.Generic.List[object]'
    $Pending = New-Object 'System.Collections.Generic.Stack[object]'
    $Pending.Push([PSCustomObject]@{ Path = $Root; Depth = 0 })
    $DirectoryCount = 0
    $EntryCount = 0

    while ($Pending.Count -gt 0) {
        $Current = $Pending.Pop()
        $DirectoryCount++
        if ($DirectoryCount -gt $MaxDirectories -or $Current.Depth -gt $MaxDepth) { throw "sessions-tree traversal bound exceeded" }
        foreach ($Item in @(Get-ChildItem -LiteralPath $Current.Path -Force -ErrorAction Stop)) {
            $EntryCount++
            if ($EntryCount -gt $MaxEntries) { throw "sessions-tree entry bound exceeded" }
            $ExactName = $Item.Name.StartsWith("rollout-", [StringComparison]::Ordinal) -and $Item.Name.EndsWith($Suffix, [StringComparison]::Ordinal)
            $Redirected = [bool]($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)
            if ($ExactName -and $Redirected) { throw "an exact rollout filename match is redirected" }
            if ($Redirected) { continue }
            if ($Item.PSIsContainer) {
                $Pending.Push([PSCustomObject]@{ Path = $Item.FullName; Depth = $Current.Depth + 1 })
                continue
            }
            if ($ExactName) {
                $Matches.Add($Item)
                if ($Matches.Count -gt 1) { return $Matches.ToArray() }
            }
        }
    }
    return $Matches.ToArray()
}

try {
    if ($ThreadId -cnotmatch '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$') { throw "ThreadId must be a lowercase UUID" }

    if (-not $SessionsDir) {
        $CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else {
            $UserHome = if ($HOME) { $HOME } else { [Environment]::GetFolderPath("UserProfile") }
            if (-not $UserHome) { throw "HOME/UserProfile is unavailable; pass -SessionsDir" }
            Join-Path $UserHome ".codex"
        }
        $SessionsDir = Join-Path $CodexHome "sessions"
    }

    $Root = Get-Item -LiteralPath $SessionsDir -Force -ErrorAction SilentlyContinue
    if (-not $Root -or -not $Root.PSIsContainer -or ($Root.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "sessions directory is unavailable or unsafe" }

    $Matches = @(Find-ExactRollouts -Root $Root.FullName -Suffix "-$ThreadId.jsonl")
    if ($Matches.Count -eq 0) { throw "no rollout filename matched the requested thread id" }
    if ($Matches.Count -ne 1) { throw "multiple rollout filenames matched the requested thread id" }

    $Rollout = Get-Item -LiteralPath $Matches[0].FullName -Force
    if ($Rollout.PSIsContainer -or ($Rollout.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "matched rollout is not a safe regular file" }
    if ($Rollout.Length -le 0 -or $Rollout.Length -gt $MaxRolloutBytes) { throw "matched rollout size is invalid" }
    $InitialLength = $Rollout.Length
    $InitialWriteTicks = $Rollout.LastWriteTimeUtc.Ticks

    # FileShare.Read prevents replacement and concurrent writes while this snapshot handle is open.
    $Stream = [IO.File]::Open($Rollout.FullName, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        if ($Stream.Length -ne $InitialLength) { throw "matched rollout changed before inspection" }
        $Utf8 = New-Object Text.UTF8Encoding($false, $true)
        $Reader = New-Object IO.StreamReader($Stream, $Utf8, $true, 4096, $true)
        try {
            $Sessions = @(); $Turns = @()
            while (($Line = $Reader.ReadLine()) -ne $null) {
                if ($Line.Length -gt $MaxLineChars) { throw "rollout contains an oversized JSONL record" }
                try { $Record = $Line | ConvertFrom-Json -ErrorAction Stop } catch { throw "rollout contains invalid JSONL" }
                $Type = Get-OptionalProperty -Object $Record -Name "type"
                $PayloadProperty = $Record.PSObject.Properties["payload"]
                if ($null -eq $PayloadProperty -or $null -eq $PayloadProperty.Value) { continue }
                if ($Type -ceq "session_meta") { $Sessions += $PayloadProperty.Value }
                elseif ($Type -ceq "turn_context") { $Turns += $PayloadProperty.Value }
            }
        }
        finally { $Reader.Dispose() }
        if ($Stream.Length -ne $InitialLength) { throw "rollout changed during inspection" }
    }
    finally { $Stream.Dispose() }

    $FinalRollout = Get-Item -LiteralPath $Rollout.FullName -Force
    if ($FinalRollout.PSIsContainer -or ($FinalRollout.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
        $FinalRollout.Length -ne $InitialLength -or $FinalRollout.LastWriteTimeUtc.Ticks -ne $InitialWriteTicks) { throw "rollout changed during inspection" }

    if ($Sessions.Count -ne 1) { throw "missing or ambiguous session metadata" }
    if ($Turns.Count -eq 0) { throw "missing turn context" }
    $Session = $Sessions[0]
    $ObservedThreadId = Get-OptionalProperty -Object $Session -Name "id"
    if ($ObservedThreadId -cne $ThreadId) { throw "session metadata does not identify the requested thread" }
    $AgentRole = Get-OptionalProperty -Object $Session -Name "agent_role"
    if (-not $AgentRole) { throw "missing agent role" }

    $Models=@(); $Efforts=@(); $Sandboxes=@(); $Permissions=@(); $WorkingDirs=@()
    foreach ($Turn in $Turns) {
        $Models += ,(Get-OptionalProperty -Object $Turn -Name "model")
        $Efforts += ,(Get-OptionalProperty -Object $Turn -Name "effort")
        $SandboxProperty = $Turn.PSObject.Properties["sandbox_policy"]
        $Sandboxes += ,($(if ($null -ne $SandboxProperty) { Get-OptionalProperty -Object $SandboxProperty.Value -Name "type" } else { $null }))
        $PermissionProperty = $Turn.PSObject.Properties["permission_profile"]
        $Permissions += ,($(if ($null -ne $PermissionProperty) { Get-OptionalProperty -Object $PermissionProperty.Value -Name "type" } else { $null }))
        $WorkingDirs += ,(Get-OptionalProperty -Object $Turn -Name "cwd")
    }

    [ordered]@{
        thread_id = $ObservedThreadId
        parent_thread_id = Get-OptionalProperty -Object $Session -Name "parent_thread_id"
        agent_role = $AgentRole
        agent_path = Get-OptionalProperty -Object $Session -Name "agent_path"
        model_provider = Get-OptionalProperty -Object $Session -Name "model_provider"
        model = Get-UniqueValue -Values $Models -Label "model"
        effort = Get-UniqueValue -Values $Efforts -Label "effort"
        sandbox_policy_type = Get-UniqueValue -Values $Sandboxes -Label "sandbox policy types" -AllowNull
        permission_profile_type = Get-UniqueValue -Values $Permissions -Label "permission profile types" -AllowNull
        cwd = Get-UniqueValue -Values $WorkingDirs -Label "working directories" -AllowNull
    } | ConvertTo-Json -Compress
}
catch {
    [Console]::Error.WriteLine("error: " + $_.Exception.Message)
    exit 1
}
