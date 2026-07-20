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

    [object]$SparkEfforts = "low,medium,high",

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

function ConvertTo-SparkEffortList {
    param([AllowNull()][object]$Value)

    $Values = @()
    foreach ($Entry in @($Value)) {
        if ($null -eq $Entry) { continue }
        foreach ($Part in ([string]$Entry).Split(",")) {
            $Normalized = $Part.Trim().ToLowerInvariant()
            if ([string]::IsNullOrWhiteSpace($Normalized)) { continue }
            if (@("low", "medium", "high") -notcontains $Normalized) {
                throw "Unsupported Spark effort value: $Part"
            }
            if ($Values -notcontains $Normalized) {
                $Values += $Normalized
            }
        }
    }
    return $Values
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
    Write-Warning "This removes package-managed AMS plugins, profiles, backups, legacy skill directories, and package-created marked user configuration."
    Write-Host "Pre-existing unmarked user configuration, unrelated files, and project-local configuration are preserved."
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

function Invoke-LocalFallbackUninstall {
    param([Parameter(Mandatory = $true)]$Python)

    $Cleaner = @'
from __future__ import annotations

import ctypes
import json
import os
import shutil
import socket
import stat
import sys
import tempfile
import time
import uuid
from pathlib import Path

MARKER = "# managed-by: adaptive-master-subagent-orchestration"
LOCK_STALE_SECONDS = 2 * 60 * 60
NAMES = (
    "adaptive-master-subagent-orchestration-option-a-two-skill",
    "adaptive-master-subagent-orchestration-option-b-unified",
    "adaptive-master-subagent-orchestration-option-c-installer-required",
    "adaptive-master-subagent-orchestration-option-a-modular",
    "adaptive-master-subagent-orchestration-option-c-lean",
    "adaptive-master-subagent-orchestration",
)
LEGACY_SKILLS = ("adaptive-master-subagent-orchestration", "ams-orchestration", "ams-installer")


def fail(message: str) -> None:
    raise SystemExit(message)


def lstat(path: Path):
    try:
        return path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        fail(f"Unable to inspect managed path {path}: {exc}")


def is_reparse(metadata) -> bool:
    attributes = getattr(metadata, "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def is_regular_file(path: Path) -> bool:
    metadata = lstat(path)
    return metadata is not None and stat.S_ISREG(metadata.st_mode) and not is_reparse(metadata)


def managed_file(path: Path) -> bool:
    if not is_regular_file(path):
        return False
    try:
        with path.open("r", encoding="utf-8", errors="strict") as handle:
            first = handle.readline().rstrip("\r\n")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"Unable to inspect package ownership marker in {path}: {exc}")
    return first == MARKER


def process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        except OSError:
            return False
        return True
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32)]
    kernel32.GetExitCodeProcess.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return ctypes.get_last_error() == 5
    try:
        exit_code = ctypes.c_uint32()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return False
        return exit_code.value == STILL_ACTIVE
    finally:
        kernel32.CloseHandle(handle)


def inspect_lock(path: Path, label: str) -> bool:
    metadata = lstat(path)
    if metadata is None:
        return False
    if not stat.S_ISREG(metadata.st_mode) or is_reparse(metadata):
        fail(f"{label} lock path is not a regular file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        data = {}
    live = (
        data.get("host") == socket.gethostname()
        and isinstance(data.get("pid"), int)
        and process_is_alive(int(data["pid"]))
    )
    age = time.time() - metadata.st_mtime
    if live or age <= LOCK_STALE_SECONDS:
        fail(f"Another AMS operation appears to be active: {path}")
    return True


def recognized(name: str) -> bool:
    return any(
        name == package
        or name.startswith(f"{package}.backup-")
        or name.startswith(f"{package}.installing-")
        or name.startswith(f".{package}.ams-uninstalling-")
        or (name.startswith(f".{package}.backup-") and ".ams-uninstalling-" in name)
        for package in NAMES
    )


def safe_children(path: Path) -> list[Path]:
    metadata = lstat(path)
    if metadata is None:
        return []
    if not stat.S_ISDIR(metadata.st_mode) or is_reparse(metadata):
        fail(f"Expected a regular directory, found another path type: {path}")
    try:
        return list(path.iterdir())
    except OSError as exc:
        fail(f"Unable to enumerate managed directory {path}: {exc}")


def collect_targets(home: Path, codex_home: Path, market_root: Path) -> list[Path]:
    targets: list[Path] = []
    plugin_root = market_root / "plugins"
    backup_root = market_root / "backups"
    for path in safe_children(plugin_root):
        if recognized(path.name):
            targets.append(path)
    for path in safe_children(backup_root):
        if recognized(path.name):
            targets.append(path)
    for path in safe_children(market_root):
        if path.name.startswith(".ams-transaction-"):
            targets.append(path)

    agents = codex_home / "agents"
    for path in safe_children(agents):
        if managed_file(path) or (path.name.startswith(".ams_") and ".ams-uninstalling-" in path.name):
            targets.append(path)

    config = codex_home / "ams-orchestration.toml"
    if managed_file(config):
        targets.append(config)
    for path in safe_children(codex_home):
        if path.name.startswith(".ams-orchestration.toml.ams-uninstalling-") and managed_file(path):
            targets.append(path)

    legacy_root = home / ".agents" / "skills"
    for name in LEGACY_SKILLS:
        path = legacy_root / name
        if lstat(path) is not None:
            targets.append(path)
    for path in safe_children(legacy_root):
        if any(path.name.startswith(f".{name}.ams-uninstalling-") for name in LEGACY_SKILLS):
            targets.append(path)

    unique: list[Path] = []
    seen: set[str] = set()
    for path in targets:
        key = os.path.normcase(os.path.abspath(path))
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def marketplace_update(path: Path) -> tuple[bytes | None, bytes | None]:
    metadata = lstat(path)
    if metadata is None:
        return None, None
    if not stat.S_ISREG(metadata.st_mode) or is_reparse(metadata):
        fail(f"Marketplace path is not a regular file: {path}")
    try:
        original = path.read_bytes()
        data = json.loads(original.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"Cannot parse existing marketplace {path}: {exc}")
    if not isinstance(data, dict):
        fail(f"Marketplace root must be a JSON object: {path}")
    plugins = data.get("plugins")
    if plugins is None:
        plugins = []
    if not isinstance(plugins, list):
        fail(f"Marketplace 'plugins' value must be a list: {path}")
    filtered = [
        item
        for item in plugins
        if not (isinstance(item, dict) and item.get("name") in NAMES)
    ]
    if filtered == plugins:
        return original, original
    data["plugins"] = filtered
    desired = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return original, desired


def atomic_write(path: Path, data: bytes) -> None:
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def make_writable(path: Path) -> None:
    try:
        metadata = path.lstat()
    except OSError:
        return
    if stat.S_ISDIR(metadata.st_mode) and not is_reparse(metadata):
        try:
            children = list(path.rglob("*"))
        except OSError:
            children = []
        for child in children:
            try:
                os.chmod(child, stat.S_IRUSR | stat.S_IWUSR | (stat.S_IXUSR if child.is_dir() else 0))
            except OSError:
                pass
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | (stat.S_IXUSR if stat.S_ISDIR(metadata.st_mode) else 0))
    except OSError:
        pass


def remove_path(path: Path) -> None:
    last_error: OSError | None = None
    for attempt in range(5):
        metadata = lstat(path)
        if metadata is None:
            return
        try:
            if stat.S_ISDIR(metadata.st_mode) and not is_reparse(metadata):
                shutil.rmtree(path)
            elif stat.S_ISDIR(metadata.st_mode):
                os.rmdir(path)
            else:
                path.unlink()
            return
        except OSError as exc:
            last_error = exc
            make_writable(path)
            time.sleep(0.1 * (attempt + 1))
    if last_error is not None:
        raise last_error


home = Path(sys.argv[1]).expanduser().resolve(strict=False)
codex_value = sys.argv[2].strip() if len(sys.argv) > 2 else ""
codex_home = (
    Path(codex_value).expanduser().resolve(strict=False)
    if codex_value
    else home / ".codex"
)
market_root = home / ".agents" / "plugins"

for lock_path, label in (
    (market_root / ".ams-install.lock", "Install"),
    (codex_home / ".agents.ams-profile-install.lock", "Profile"),
    (codex_home / ".ams-orchestration-config.lock", "Intensity"),
):
    if inspect_lock(lock_path, label):
        try:
            lock_path.unlink()
        except OSError as exc:
            fail(f"Unable to remove stale {label.lower()} lock path {lock_path}: {exc}")

targets = collect_targets(home, codex_home, market_root)
marketplace_path = market_root / "marketplace.json"
marketplace_before, marketplace_after = marketplace_update(marketplace_path)

if not targets and marketplace_before == marketplace_after:
    print("No package-managed AMS installation was found.")
    raise SystemExit(0)

token = uuid.uuid4().hex
staged: list[tuple[Path, Path]] = []
marketplace_written = False
try:
    for target in targets:
        staged_path = target.with_name(f".{target.name}.ams-uninstalling-{token}")
        if lstat(staged_path) is not None:
            fail(f"Uninstall staging path already exists: {staged_path}")
        try:
            os.replace(target, staged_path)
        except OSError as exc:
            fail(f"Unable to stage managed path {target} for removal: {exc}")
        staged.append((target, staged_path))
    if marketplace_before is not None and marketplace_after != marketplace_before:
        atomic_write(marketplace_path, marketplace_after or b"")
        marketplace_written = True
except BaseException as exc:
    errors: list[str] = []
    for original, staged_path in reversed(staged):
        try:
            if lstat(staged_path) is not None:
                if lstat(original) is not None:
                    raise RuntimeError(f"rollback refused to overwrite concurrent path: {original}")
                os.replace(staged_path, original)
        except Exception as restore_exc:
            errors.append(f"restore {original}: {restore_exc}")
    if marketplace_written and marketplace_before is not None:
        try:
            if marketplace_path.read_bytes() != marketplace_after:
                raise RuntimeError("rollback refused to overwrite a concurrent marketplace change")
            atomic_write(marketplace_path, marketplace_before)
        except Exception as restore_exc:
            errors.append(f"restore {marketplace_path}: {restore_exc}")
    if errors:
        fail(f"Fallback uninstall failed: {exc}; rollback also reported: {'; '.join(errors)}")
    raise

cleanup_errors: list[str] = []
for _, staged_path in staged:
    try:
        remove_path(staged_path)
    except OSError as exc:
        cleanup_errors.append(f"{staged_path}: {exc}")
if cleanup_errors:
    print(
        "warning: fallback uninstall completed, but staged paths remain for a later removal: "
        + "; ".join(cleanup_errors),
        file=sys.stderr,
    )

print("Fallback uninstall complete.")
'@

    $CleanerPath = Join-Path ([System.IO.Path]::GetTempPath()) ("ams-fallback-uninstall-" + [Guid]::NewGuid().ToString("N") + ".py")
    $Utf8NoBom = New-Object System.Text.UTF8Encoding -ArgumentList $false
    [System.IO.File]::WriteAllText($CleanerPath, $Cleaner, $Utf8NoBom)
    try {
        Invoke-ResolvedPython -Python $Python -Arguments @($CleanerPath, $HomeDirectory, [string]$env:CODEX_HOME)
    }
    finally {
        Remove-Item -LiteralPath $CleanerPath -Force -ErrorAction SilentlyContinue
    }
}

function Get-InstalledUninstaller {
    param([Parameter(Mandatory = $true)]$Python)
    $Finder = @'
from pathlib import Path
import stat
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
unsafe = []

def regular_uninstaller(candidate):
    try:
        relative = candidate.relative_to(home)
    except ValueError:
        unsafe.append(candidate)
        return False
    current = home
    for part in relative.parts:
        current = current / part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            return False
        except OSError:
            unsafe.append(candidate)
            return False
        if stat.S_ISLNK(metadata.st_mode):
            unsafe.append(candidate)
            return False
    if not stat.S_ISREG(metadata.st_mode):
        if candidate.exists():
            unsafe.append(candidate)
        return False
    return True

plugin_root = home / ".agents" / "plugins" / "plugins"
for name in names:
    candidate = plugin_root / name / "scripts" / "install_package.py"
    if regular_uninstaller(candidate):
        print(candidate)
        raise SystemExit(0)
backup_root = home / ".agents" / "plugins" / "backups"
for name in names:
    for backup in sorted(backup_root.glob(f"{name}.backup-*"), reverse=True):
        candidate = backup / "scripts" / "install_package.py"
        if regular_uninstaller(candidate):
            print(candidate)
            raise SystemExit(0)
if unsafe:
    print(f"Unsafe AMS uninstaller path was refused: {unsafe[0]}", file=sys.stderr)
    raise SystemExit(4)
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
    $Details = (($Output | ForEach-Object { [string]$_ }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($Details)) {
        throw "Installed AMS uninstaller discovery failed with exit code $Code."
    }
    throw "Installed AMS uninstaller discovery failed with exit code $Code. $Details"
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
    if (-not $PSBoundParameters.ContainsKey("Intensity") -and -not [string]::IsNullOrWhiteSpace($env:AMS_INTENSITY)) {
        $EnvironmentIntensity = $env:AMS_INTENSITY.Trim().ToLowerInvariant()
        if (@("auto", "minimal", "moderate", "heavy", "extreme") -notcontains $EnvironmentIntensity) {
            throw "Unsupported AMS_INTENSITY value: $($env:AMS_INTENSITY)"
        }
        $Intensity = $EnvironmentIntensity
    }
    if (-not $PSBoundParameters.ContainsKey("SparkEfforts") -and -not [string]::IsNullOrWhiteSpace($env:AMS_SPARK_EFFORTS)) {
        $SparkEfforts = $env:AMS_SPARK_EFFORTS
    }
    $SparkEffortValues = @(ConvertTo-SparkEffortList -Value $SparkEfforts)
    if ($env:AMS_EXCLUDE_SPARK -notin @($null, "", "0", "1")) {
        throw "AMS_EXCLUDE_SPARK must be 0 or 1; received: $($env:AMS_EXCLUDE_SPARK)"
    }
    if ($env:AMS_UNINSTALL_FORCE -notin @($null, "", "0", "1")) {
        throw "AMS_UNINSTALL_FORCE must be 0 or 1; received: $($env:AMS_UNINSTALL_FORCE)"
    }
    if (-not ($ExcludeSpark -or $env:AMS_EXCLUDE_SPARK -eq "1") -and $SparkEffortValues.Count -eq 0) {
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
        Write-Heading "Removing orphaned Adaptive Master-Subagent managed state"
        Invoke-LocalFallbackUninstall -Python $Python
        Write-Host ""
        Write-Host "Uninstall completed successfully. Restart Codex to refresh discovered plugins and agents." -ForegroundColor Green
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
            $Arguments = @($Installer, "--home", $HomeDirectory, "--upgrade-managed", "--intensity", $Intensity, "--spark-efforts", ($SparkEffortValues -join ","))
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
