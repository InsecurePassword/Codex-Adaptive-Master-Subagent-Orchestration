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
        Get-Item -LiteralPath (Join-Path $Root "VERSION")
        Get-Item -LiteralPath (Join-Path $Root "deploy.ps1")
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
        if ([int]$Matches[1] -ne 1) { throw "Existing agents.max_depv\È	
	X]Ú\ÖÌWJNÈSTÈ™\]Z\™\ÈKˆˆBˆ™]\›‚ˆBˆ	YÙ[ÙXİ[ÛœÈHÜ™YÙ^N“X]Ú\Ê	^	ÊÛJW—Ê—ØYÙ[×WÊ‰	ÊBˆYˆ
	YÙ[ÙXİ[ÛœËÛİ[YİJHÈ›İÈÛÙ^ÛÛ™šYİ\˜][ÛˆÛÛZ[œÈ][\HØYÙ[×HÙXİ[ÛœËˆˆBˆYˆ
	YÙ[ÙXİ[ÛœËÛİ[Y\HJHÂˆ	^HÜ™YÙ^N”™\XÙJ	^	ÊÛJWŠÊ—ØYÙ[×WÊŠI	Ë˜	X›X^Ù\HH	X[˜YÙYX\šÙ\ˆŠBˆBˆ[ÙHÂˆ	^H	^•š[Q[™

H
È˜˜–ØYÙ[×X›X^Ù\HH	X[˜YÙYX\šÙ\˜ˆ‚ˆBˆÜš]KU]	]	^ŸB‚™[˜İ[Ûˆ™[[İ™KSX[˜YÙYX^\
Üİš[™×I]
HÂˆYˆ
[›İ
\İT]	]T]\HXYŠJHÈ™]\›ˆBˆ	^H™XYU]	]ˆ	^HÜ™YÙ^N”™\XÙJ	^	ÊÛJW—Ê›X^Ù\ÊWÊŒWÊˆ×Ê›X[˜YÙYXN—Ê˜Y\]™K[X\İ\‹\İX˜YÙ[[Ü˜Ú\İ˜][Û—Ê—×ÉË	ÉÊBˆ	^HÜ™YÙ^N”™\XÙJ	^	ÊÛ\ÊW—Ê—ØYÙ[×WÊ—×ŠÏWÊŠÎ—Ö×—WJ×_ŠJIË	ÉÊBˆYˆ
	^•š[J
JHÈÜš]KU]	]
	^•š[Q[™

H
È˜ˆŠHH[ÙHÈ™[[İ™KR][H	]Q›Ü˜ÙHBŸB‚™[˜İ[Ûˆ[œİ[P[\ÊÜİš[™×IÛİ\˜ÙT›ÛİÜİš[™×IÛYKÜİš[™×IÛÙ^ÛYKÜİš[™Ö×WIÜ\šËØ›ÛÛI›ÔÜ\šËØ›ÛÛI[[œÚ]TÜXÚYšYY
HÂˆ˜[Y]KTÛİ\˜ÙH	Ûİ\˜ÙT›Ûİ‚ˆ	^[ØY›ÛİH›Ú[‹T]	Ûİ\˜ÙT›Ûİ	^[ØY\™XİÜBˆ	ÚÚ[Ûİ\˜ÙHH›Ú[‹T]	^[ØY›ÛİœÚÚ[×[\Ë[Ü˜Ú\İ˜][Ûˆ‚ˆ	›Ùš[TÛİ\˜ÙHH›Ú[‹T]	^[ØY›Ûİ˜\ÜÙ]×YÙ[\›Ùš[\È‚ˆ	ÚÚ[\™Ù]H›Ú[‹T]	ÛYH‹˜YÙ[×ÚÚ[×[\Ë[Ü˜Ú\İ˜][Ûˆ‚ˆ	YÙ[\™Ù]H›Ú[‹T]	ÛÙ^ÛYH˜YÙ[È‚ˆ	[[œÚ]U\™Ù]H›Ú[‹T]	ÛÙ^ÛYH˜[\Ë[Ü˜Ú\İ˜][Û‹Û[‚ˆ	ÛÛ™šYÕ\™Ù]H›Ú[‹T]	ÛÙ^ÛYH˜ÛÛ™šYËÛ[‚ˆ	˜XÚİ\›ÛİH›Ú[‹T]	ÛYH‹˜YÙ[×[\Ë[Ü˜Ú\İ˜][Û—˜XÚİ\È‚ˆ	\Ú\™YH
Ù]Q\Ú\™Y›Ùš[\È	Ü\šÈ	›ÔÜ\šÊB‚ˆYˆ

\İT]	ÚÚ[\™Ù]
HX[™[›İ
\İSX[˜YÙYÚÚ[	ÚÚ[\™Ù]
JHÈ›İÈ”™Y\Ú[™ÈÈ™\XÙH[›İÛ™YÚÚ[ˆ	ÚÚ[\™Ù]ˆBˆ›Ü™XXÚ
	Ûİ\˜ÙH[ˆÙ]PÚ[][H
›Ú[‹T]	›Ùš[TÛİ\˜ÙH˜[\×Ê‹Û[ŠHQš[JHÂˆ	\™Ù]H›Ú[‹T]	YÙ[\™Ù]	Ûİ\˜ÙK“˜[YBˆYˆ

	\Ú\™YXÛÛZ[œÈ	Ûİ\˜ÙK˜\ÙS˜[YJHX[™
\İT]	\™Ù]
HX[™[›İ
\İSX[˜YÙYš[H	\™Ù]
JHÂˆ›İÈ”™Y\Ú[™ÈÈ™\XÙH[›İÛ™Y›Ùš[Nˆ	\™Ù]‚ˆBˆBˆYˆ

\İT]	[[œÚ]U\™Ù]
HX[™[›İ
\İSX[˜YÙYš[H	[[œÚ]U\™Ù]
HX[™	[[œÚ]TÜXÚYšYY
HÂˆ›İÈ”™Y\Ú[™ÈÈ[ÙYH[›İÛ™Y[[œÚ]HÛÛ™šYİ\˜][Ûˆ	[[œÚ]U\™Ù]‚ˆB‚ˆ	^\İ[™Ò[[œÚ]HHYˆ
\İT]	[[œÚ]U\™Ù]T]\HXYŠHÈÙ]R[[œÚ]U˜[YH
™XYU]	[[œÚ]U\™Ù]
HH[ÙHÈ	[Bˆ	™\ÛÛ™Y[[œÚ]HHYˆ
	[[œÚ]TÜXÚYšYY
HÈ	[[œÚ]HH[ÙZYˆ
	^\İ[™Ò[[œÚ]JHÈ	^\İ[™Ò[[œÚ]HH[ÙHÈ˜]]ÈˆB‚ˆÜš]KRÜİ”ÚÚ[ˆ	ÚÚ[\™Ù]‚ˆÜš]KRÜİ”›Ùš[\Îˆ	
	\Ú\™YÛİ[
H‚ˆÜš]KRÜİ’[[œÚ]Nˆ	™\ÛÛ™Y[[œÚ]H‚ˆYˆ
	Ú]Y”™Y™\™[˜ÙJHÈÜš]KRÜİ•Ú]Yˆ›ÈÚ[™Ù\ÈXYKˆÈ™]\›ˆB‚ˆ	™\]Z\™Y\™XİÜšY\ÈH

Ü]T]	ÚÚ[\™Ù]T\™[
K	YÙ[\™Ù]	ÛÙ^ÛYJBˆ™]ËR][HR][U\H\™XİÜHT]	™\]Z\™Y\™XİÜšY\ÈQ›Ü˜ÙHİ]S[ˆ˜XÚİ\R][H	ÚÚ[\™Ù]	˜XÚİ\›ÛİˆYˆ
\İT]	ÚÚ[\™Ù]
HÈ™[[İ™KR][H	ÚÚ[\™Ù]T™Xİ\œÙHQ›Ü˜ÙHBˆÛÜKR][H	ÚÚ[Ûİ\˜ÙHQ\İ[˜][Ûˆ	ÚÚ[\™Ù]T™Xİ\œÙHQ›Ü˜ÙBˆÔŞ\İ[K’SË‘š[WN•Üš]P[^

›Ú[‹T]	ÚÚ[\™Ù]‹˜[\Ë[X[˜YÙYŠK˜Y\]™K[X\İ\‹\İX˜YÙ[[Ü˜Ú\İ˜][Û˜™\œÚ[ÛI™\œÚ[Û˜ˆ‹	]›Ğ›ÛJB‚ˆ›Ü™XXÚ
	Ûİ\˜ÙH[ˆÙ]PÚ[][H
›Ú[‹T]	›Ùš[TÛİ\˜ÙH˜[\×Ê‹Û[ŠHQš[JHÂˆ	˜[YHH	Ûİ\˜ÙK˜\ÙS˜[YBˆ	\™Ù]H›Ú[‹T]	YÙ[\™Ù]	Ûİ\˜ÙK“˜[YBˆYˆ
	\Ú\™YXÛÛZ[œÈ	˜[YJHÂˆ˜XÚİ\R][H	\™Ù]	˜XÚİ\›ÛİˆÛÜKR][H	Ûİ\˜ÙK‘[˜[YHQ\İ[˜][Ûˆ	\™Ù]Q›Ü˜ÙBˆBˆ[ÙZYˆ

\İT]	\™Ù]
HX[™
\İSX[˜YÙYš[H	\™Ù]
JHÂˆ˜XÚİ\R][H	\™Ù]	˜XÚİ\›Ûİˆ™[[İ™KR][H	\™Ù]Q›Ü˜ÙBˆBˆB‚ˆYˆ
[›İ
\İT]	[[œÚ]U\™Ù]
H[Üˆ
\İSX[˜YÙYš[H	[[œÚ]U\™Ù]
JHÂˆÜš]KU]	[[œÚ]U\™Ù]‰X[˜YÙYX\šÙ\˜œØÚ[XWİ™\œÚ[ÛˆHXš[[œÚ]HH‰™\ÛÛ™Y[[œÚ]X˜ˆ‚ˆBˆ[œİ\™KSX^\	ÛÛ™šYÕ\™Ù]‚ˆYˆ
[›İ
\İSX[˜YÙYÚÚ[	ÚÚ[\™Ù]
JHÈ›İÈ”ÚÚ[™\šYšXØ][Ûˆ˜Z[YˆˆBˆYˆ

™XYU]
›Ú[‹T]	ÚÚ[\™Ù]˜YÙ[×Ü[˜ZKX[[ŠJH[›İX]Ú	Ø[İ×Ú[\XÚ]Ú[›ØØ][Û—ÊYIÊHÈ›İÈ’[\XÚ][›ØØ][Ûˆ™\šYšXØ][Ûˆ˜Z[YˆˆBˆ›Ü™XXÚ
	˜[YH[ˆ	\Ú\™Y
HÂˆYˆ
[›İ
\İSX[˜YÙYš[H
›Ú[‹T]	YÙ[\™Ù]
	˜[YH
È‹Û[ŠJJJHÈ›İÈ”›Ùš[H™\šYšXØ][Ûˆ˜Z[Yˆ	˜[YHˆBˆBˆÜš]KRÜİ‰Xİ[ÛˆÛÛ\]YİXØÙ\ÜÙ[KˆˆQ›Ü™YÜ›İ[™ÛÛÜˆÜ™Y[‚ŸB‚™[˜İ[Ûˆ[š[œİ[P[\ÊÜİš[™×IÛYKÜİš[™×IÛÙ^ÛYJHÂˆYˆ
[›İ	›Ü˜ÙHX[™	[ST×ÕS’S”ÕSÑ“ÔÑH[™HŒHŠHÂˆÜš]KUØ\›š[™È•\È™[[İ™\ÈXÚØYÙK[X[˜YÙYSTÈš[\È[™ÛÛ™šYİ\˜][Û‹ˆ‚ˆYˆ

™XYRÜİ•\H‘SSÕ‘HÈÛÛ[YHŠHXÛ™H”‘SSÕ‘HŠHÈÜš]KRÜİ•[š[œİ[Ø[˜Ù[YˆÈ™]\›ˆBˆBˆ	ÚÚ[\™Ù]H›Ú[‹T]	ÛYH‹˜YÙ[×ÚÚ[×[\Ë[Ü˜Ú\İ˜][Ûˆ‚ˆ	YÙ[\™Ù]H›Ú[‹T]	ÛÙ^ÛYH˜YÙ[È‚ˆ	[[œÚ]U\™Ù]H›Ú[‹T]	ÛÙ^ÛYH˜[\Ë[Ü˜Ú\İ˜][Û‹Û[‚ˆ	ÛÛ™šYÕ\™Ù]H›Ú[‹T]	ÛÙ^ÛYH˜ÛÛ™šYËÛ[‚ˆ	İ]T›ÛİH›Ú[‹T]	ÛYH‹˜YÙ[×[\Ë[Ü˜Ú\İ˜][Ûˆ‚‚ˆYˆ
	Ú]Y”™Y™\™[˜ÙJHÈÜš]KRÜİ•Ú]YˆX[˜YÙYSTÈš[\ÈÛİ[™H™[[İ™YˆÈ™]\›ˆBˆYˆ

\İT]	ÚÚ[\™Ù]
HX[™
\İSX[˜YÙYÚÚ[	ÚÚ[\™Ù]
JHÈ™[[İ™KR][H	ÚÚ[\™Ù]T™Xİ\œÙHQ›Ü˜ÙHBˆYˆ
\İT]	YÙ[\™Ù]T]\HÛÛZ[™\ŠHÂˆ›Ü™XXÚ
	›Ùš[H[ˆÙ]PÚ[][H
›Ú[‹T]	YÙ[\™Ù]˜[\×Ê‹Û[ŠHQš[HQ\œ›ÜXİ[ÛˆÚ[[PÛÛ[YJHÂˆYˆ
\İSX[˜YÙYš[H	›Ùš[K‘[˜[YJHÈ™[[İ™KR][H	›Ùš[K‘[˜[YHQ›Ü˜ÙHBˆBˆBˆYˆ

\İT]	[[œÚ]U\™Ù]
HX[™
\İSX[˜YÙYš[H	[[œÚ]U\™Ù]
JHÈ™[[İ™KR][H	[[œÚ]U\™Ù]Q›Ü˜ÙHBˆ™[[İ™KSX[˜YÙYX^\	ÛÛ™šYÕ\™Ù]ˆYˆ
\İT]	İ]T›Ûİ
HÈ™[[İ™KR][H	İ]T›ÛİT™Xİ\œÙHQ›Ü˜ÙHBˆÜš]KRÜİ•[š[œİ[ÛÛ\]YİXØÙ\ÜÙ[KˆˆQ›Ü™YÜ›İ[™ÛÛÜˆÜ™Y[‚ŸB‚HÂˆYˆ
[›İ	Ğ›İ[™\˜[Y]\œËÛÛZ[œÒÙ^JXİ[ÛˆŠHX[™	[ST×ĞPÕSÓŠHÂˆİÚ]Ú
	[ST×ĞPÕSÓ‹•š[J
K•ÓİÙ\’[˜\šX[

JHÂˆš[œİ[ˆÈ	Xİ[ÛˆH’[œİ[ˆBˆœ™\Z\ˆˆÈ	Xİ[ÛˆH”™\Z\ˆˆBˆ[š[œİ[ˆÈ	Xİ[ÛˆH•[š[œİ[ˆBˆY˜][È›İÈ•[œİ\ÜYST×ĞPÕSÓˆ	
	[ST×ĞPÕSÓŠHˆBˆBˆBˆ	[[œÚ]TÜXÚYšYYH	Ğ›İ[™\˜[Y]\œËÛÛZ[œÒÙ^J’[[œÚ]HŠBˆYˆ
[›İ	[[œÚ]TÜXÚYšYYX[™	[ST×ÒS•S”ÒUJHÂˆ	[[œÚ]HH	[ST×ÒS•S”ÒUK•š[J
K•ÓİÙ\’[˜\šX[

BˆYˆ
	˜[Y[[œÚ]Y\È[›İÛÛZ[œÈ	[[œÚ]JHÈ›İÈ•[œİ\ÜYST×ÒS•S”ÒUNˆ	[[œÚ]HˆBˆ	[[œÚ]TÜXÚYšYYH	YBˆBˆYˆ
[›İ	Ğ›İ[™\˜[Y]\œËÛÛZ[œÒÙ^J”Ü\šÑY™›ÜÈŠHX[™	[ST×ÔÔT’×ÑQ‘“Ô•ÊHÈ	Ü\šÑY™›ÜÈH	[ST×ÔÔT’×ÑQ‘“Ô•ÈBˆYˆ
[›İ	Ğ›İ[™\˜[Y]\œËÛÛZ[œÒÙ^J’ÛYQ\™XİÜHŠHX[™	[ST×ÒÓQJHÈ	ÛYQ\™XİÜHH	[ST×ÒÓQHB‚ˆ	ÛYQ\™XİÜHHÙ]Q[]	ÛYQ\™XİÜBˆ	ÛÙ^ÛYHHYˆ
	[ÓÑVÒÓQJHÈÙ]Q[]	[ÓÑVÒÓQHH[ÙHÈ›Ú[‹T]	ÛYQ\™XİÜH‹˜ÛÙ^ˆBˆ	Ü\šÈH
ÛÛ™\TÜ\šÑY™›ÜÈ	Ü\šÑY™›ÜÊBˆ	›ÔÜ\šÈH	^ÛYTÜ\šÈ[Üˆ	[ST×ÑVÓQWÔÔT’ÈY\HŒH‚ˆYˆ
[›İ	›ÔÜ\šÈX[™	Ü\šËÛİ[Y\H
HÈ›İÈ”Ü\šÑY™›ÜÈØ[››İ™H[\H[›\ÜÈÜ\šÈ\È^ÛYYˆˆB‚ˆYˆ
[›İ	Ú]Y”™Y™\™[˜ÙJHÂˆ	ØÚÔ]H›Ú[‹T]	ÛYQ\™XİÜH‹˜YÙ[×˜[\Ë[Ü˜Ú\İ˜][Û‹Y\ŞK›ØÚÈ‚ˆ[\‹SØÚÈ	ØÚÔ]ˆBˆHÂˆYˆ
	Xİ[ÛˆY\H•[š[œİ[ŠHÂˆÜš]KRXY[™È•[š[œİ[[™ÈY\]™HX\İ\‹TİX˜YÙ[Ü˜Ú\İ˜][Ûˆ‚ˆ[š[œİ[P[\È	ÛYQ\™XİÜH	ÛÙ^ÛYBˆBˆ[ÙHÂˆYˆ
	Ûİ\˜ÙQ\™XİÜJHÂˆ	Ûİ\˜ÙT›ÛİHÙ]Q[]	Ûİ\˜ÙQ\™XİÜBˆBˆ[ÙHÂˆ	™YˆHYˆ
	™\ÜÚ]ÜT™YŠHÈ	™\ÜÚ]ÜT™Y‹•š[J
HH[ÙZYˆ
	[ST×Ô‘QŠHÈ	[ST×Ô‘Q‹•š[J
HH[ÙHÈ›XZ[ˆˆBˆYˆ
	™Yˆ[›İX]Ú	×–ĞKV˜K^ŒNK—ËËWJÉ	È[Üˆ	™Y‹ÛÛZ[œÊ‹‹ˆŠJHÈ›İÈ•[œİ\ÜY™\ÜÚ]ÜH™Yˆ	™YˆˆBˆ	Ûİ\˜ÙT›ÛİHİÛ›ØYTÛİ\˜ÙH	™Yˆ	\˜Ú]™T]ˆBˆÜš]KRXY[™È
ÌZ[™ÈY\]™HX\İ\‹TİX˜YÙ[Ü˜Ú\İ˜][ÛˆˆYˆ	Xİ[ÛŠBˆ[œİ[P[\È	Ûİ\˜ÙT›Ûİ	ÛYQ\™XİÜH	ÛÙ^ÛYH	Ü\šÈ	›ÔÜ\šÈ	[[œÚ]TÜXÚYšYYˆBˆBˆš[˜[HÈ^]SØÚÈBŸB˜Ø]ÚÂˆ^]SØÚÂˆÜš]KQ\œ›Üˆ	Ë‘^Ù\[Û‹“Y\ÜØYÙBˆ^]BŸB™š[˜[HÂˆYˆ
	[\›ÛİX[™
\İT]	[\›Ûİ
JHÈ™[[İ™KR][H	[\›ÛİT™Xİ\œÙHQ›Ü˜ÙHQ\œ›ÜXİ[ÛˆÚ[[PÛÛ[YHBŸB