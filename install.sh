#!/bin/sh
# Adaptive Master-Subagent Orchestration installer
# Version 3.1.0

set -eu

REPOSITORY="InsecurePassword/adaptive-master-subagent-orchestration"
REF="${AMS_REF:-main}"
INSTALL_HOME="${AMS_HOME:-$HOME}"
SELECTED="${AMS_INSTALL_OPTION:-}"
INTENSITY="${AMS_INTENSITY:-auto}"
SPARK_EFFORTS="${AMS_SPARK_EFFORTS:-low,medium,high}"
EXCLUDE_SPARK="${AMS_EXCLUDE_SPARK:-0}"
FORCE_UNINSTALL="${AMS_UNINSTALL_FORCE:-0}"
ARCHIVE_SOURCE="${AMS_ARCHIVE_PATH:-}"
CONNECT_TIMEOUT="${AMS_CONNECT_TIMEOUT_SECONDS:-15}"
DOWNLOAD_TIMEOUT="${AMS_DOWNLOAD_TIMEOUT_SECONDS:-120}"
TEMP_ROOT=""

cleanup() {
    if [ -n "$TEMP_ROOT" ] && [ -d "$TEMP_ROOT" ]; then
        rm -rf "$TEMP_ROOT"
    fi
}
trap cleanup EXIT HUP INT TERM

fail() {
    printf '%s\n' "$*" >&2
    exit 1
}

usage() {
    cat <<'EOF'
Usage: install.sh [OPTION] [arguments]

OPTION may be A, B, C, UNINSTALL, or 1-4. When omitted, an interactive menu is shown.

Arguments:
  -o, --option VALUE          Bypass the menu and select A, B, C, or UNINSTALL
      --home PATH             Installation home directory (default: $HOME)
      --intensity MODE        auto|minimal|moderate|heavy|extreme
      --spark-efforts LIST    Comma-separated low,medium,high values
      --exclude-spark         Do not install optional Spark profiles
  -f, --force                 Confirm non-interactive uninstall
      --archive-path FILE     Use a local repository ZIP instead of downloading
      --ref REF               Repository branch/ref to download (default: main)
  -h, --help                  Show this help

Equivalent environment variables:
  AMS_INSTALL_OPTION, AMS_HOME, AMS_INTENSITY, AMS_SPARK_EFFORTS,
  AMS_EXCLUDE_SPARK, AMS_UNINSTALL_FORCE, AMS_ARCHIVE_PATH, AMS_REF,
  AMS_CONNECT_TIMEOUT_SECONDS, AMS_DOWNLOAD_TIMEOUT_SECONDS, GITHUB_TOKEN
EOF
}

heading() {
    printf '\n%s\n' "$1"
    printf '%s\n' "$1" | sed 's/./=/g'
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

validate_positive_integer() {
    case "$2" in
        ''|*[!0-9]*|0) fail "$1 must be a positive integer; received: $2" ;;
    esac
}

normalize_option() {
    value=$(printf '%s' "$1" | tr '[:lower:]' '[:upper:]')
    case "$value" in
        1|A) printf '%s\n' A ;;
        2|B) printf '%s\n' B ;;
        3|C) printf '%s\n' C ;;
        4|UNINSTALL|REMOVE) printf '%s\n' UNINSTALL ;;
        *) fail "Unsupported selection: $1" ;;
    esac
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        -o|--option)
            [ "$#" -ge 2 ] || fail "$1 requires a value"
            SELECTED=$2
            shift 2
            ;;
        --home)
            [ "$#" -ge 2 ] || fail "$1 requires a path"
            INSTALL_HOME=$2
            shift 2
            ;;
        --intensity)
            [ "$#" -ge 2 ] || fail "$1 requires a value"
            INTENSITY=$2
            shift 2
            ;;
        --spark-efforts)
            [ "$#" -ge 2 ] || fail "$1 requires a value"
            SPARK_EFFORTS=$2
            shift 2
            ;;
        --exclude-spark)
            EXCLUDE_SPARK=1
            shift
            ;;
        -f|--force)
            FORCE_UNINSTALL=1
            shift
            ;;
        --archive-path)
            [ "$#" -ge 2 ] || fail "$1 requires a path"
            ARCHIVE_SOURCE=$2
            shift 2
            ;;
        --ref)
            [ "$#" -ge 2 ] || fail "$1 requires a value"
            REF=$2
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            break
            ;;
        -*) fail "Unknown argument: $1" ;;
        *)
            [ -z "$SELECTED" ] || fail "Multiple installation options were supplied"
            SELECTED=$1
            shift
            ;;
    esac
done
[ "$#" -eq 0 ] || fail "Unexpected argument: $1"

prompt_selection() {
    if ! (: </dev/tty) 2>/dev/null; then
        fail "Interactive input is unavailable. Use --option A, B, C, or UNINSTALL."
    fi
    heading "Adaptive Master-Subagent Orchestration" >/dev/tty
    cat >/dev/tty <<'MENU'
Choose one installation option:

  1) Option A - Installer skill + permanent runtime (Recommended)
  2) Option B - Unified skill with conditional bootstrap
  3) Option C - Lean runtime with mandatory deterministic installation
  4) Uninstall Adaptive Master-Subagent Orchestration

MENU
    printf '%s' "Selection [1]: " >/dev/tty
    IFS= read -r choice </dev/tty || choice=""
    [ -n "$choice" ] || choice=1
    normalize_option "$choice"
}

confirm_uninstall() {
    if [ "$FORCE_UNINSTALL" = 1 ]; then
        return 0
    fi
    if ! (: </dev/tty) 2>/dev/null; then
        fail "Uninstall requires confirmation. Use --force for non-interactive removal."
    fi
    cat >/dev/tty <<'NOTICE'
This removes package-managed AMS plugins, profiles, backups, legacy skill directories,
and the user-level AMS configuration. Unrelated files and project-local configuration
are preserved.
NOTICE
    printf '%s' "Type REMOVE to continue: " >/dev/tty
    IFS= read -r confirmation </dev/tty || confirmation=""
    [ "$confirmation" = REMOVE ]
}

require_python311() {
    require_command python3
    python3 -I -S -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' \
        || fail "Python 3.11 or later is required."
}

validate_settings() {
    case "$INTENSITY" in auto|minimal|moderate|heavy|extreme) ;;
        *) fail "Unsupported intensity: $INTENSITY" ;;
    esac
    old_ifs=$IFS
    IFS=,
    # Deliberate field splitting on comma-separated values.
    set -- $SPARK_EFFORTS
    IFS=$old_ifs
    [ "$#" -gt 0 ] || fail "Spark effort list cannot be empty"
    for effort in "$@"; do
        trimmed=$(printf '%s' "$effort" | tr -d '[:space:]')
        case "$trimmed" in low|medium|high) ;; *) fail "Unsupported Spark effort: $trimmed" ;; esac
    done
    case "$EXCLUDE_SPARK" in 0|1) ;; *) fail "AMS_EXCLUDE_SPARK must be 0 or 1" ;; esac
    case "$FORCE_UNINSTALL" in 0|1) ;; *) fail "AMS_UNINSTALL_FORCE must be 0 or 1" ;; esac
    validate_positive_integer AMS_CONNECT_TIMEOUT_SECONDS "$CONNECT_TIMEOUT"
    validate_positive_integer AMS_DOWNLOAD_TIMEOUT_SECONDS "$DOWNLOAD_TIMEOUT"
    case "$REF" in
        ''|/*|*'..'*|*[!A-Za-z0-9._/-]*) fail "Unsupported repository ref: $REF" ;;
    esac
}

prepare_archive() {
    destination=$1
    if [ -n "$ARCHIVE_SOURCE" ]; then
        [ -f "$ARCHIVE_SOURCE" ] || fail "Archive path is not a readable file: $ARCHIVE_SOURCE"
        cp "$ARCHIVE_SOURCE" "$destination"
        printf 'Using repository archive: %s\n' "$ARCHIVE_SOURCE"
        return 0
    fi

    require_command curl
    archive_url="https://github.com/${REPOSITORY}/archive/refs/heads/${REF}.zip"
    api_archive_url="https://api.github.com/repos/${REPOSITORY}/zipball/${REF}"
    printf 'Downloading repository package for ref %s.\n' "$REF"
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        curl -fL --silent --show-error --retry 3 --retry-delay 1 \
            --connect-timeout "$CONNECT_TIMEOUT" --max-time "$DOWNLOAD_TIMEOUT" \
            -H "Authorization: Bearer $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "$api_archive_url" -o "$destination" \
            || fail "Repository package download failed. Verify connectivity and repository access."
    else
        curl -fL --silent --show-error --retry 3 --retry-delay 1 \
            --connect-timeout "$CONNECT_TIMEOUT" --max-time "$DOWNLOAD_TIMEOUT" \
            "$archive_url" -o "$destination" \
            || fail "Repository package download failed. Verify connectivity and repository access."
    fi
    [ -s "$destination" ] || fail "Repository package download produced an empty file."
}

safe_extract() {
    archive=$1
    destination=$2
    python3 -I -S - "$archive" "$destination" <<'PY'
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
seen: set[str] = set()
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
PY
}

find_package_root() {
    extract_path=$1
    option_dir=$2
    python3 -I -S - "$extract_path" "$option_dir" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
name = sys.argv[2]
matches = [path for path in root.rglob(name) if path.is_dir() and path.name == name]
if len(matches) != 1:
    raise SystemExit(f"Expected exactly one package directory named {name} after extraction; found {len(matches)}.")
print(matches[0])
PY
}

find_installed_uninstaller() {
    plugin_root="$INSTALL_HOME/.agents/plugins/plugins"
    [ -d "$plugin_root" ] || return 1
    for name in \
        adaptive-master-subagent-orchestration-option-a-two-skill \
        adaptive-master-subagent-orchestration-option-b-unified \
        adaptive-master-subagent-orchestration-option-c-installer-required \
        adaptive-master-subagent-orchestration-option-a-modular \
        adaptive-master-subagent-orchestration-option-c-lean \
        adaptive-master-subagent-orchestration
    do
        candidate="$plugin_root/$name/scripts/install_package.py"
        if [ -f "$candidate" ] && [ ! -L "$candidate" ]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done
    return 1
}

run_package_operation() {
    installer=$1
    selected=$2
    if [ "$selected" = UNINSTALL ]; then
        python3 -B -E -s -S "$installer" --home "$INSTALL_HOME" --uninstall --yes
        return
    fi

    set -- --home "$INSTALL_HOME" --upgrade-managed --intensity "$INTENSITY" --spark-efforts "$SPARK_EFFORTS"
    if [ "$EXCLUDE_SPARK" = 1 ]; then
        set -- "$@" --exclude-spark
    fi
    python3 -B -E -s -S "$installer" "$@"
}

if [ -n "$SELECTED" ]; then
    SELECTED=$(normalize_option "$SELECTED")
else
    SELECTED=$(prompt_selection)
fi
validate_settings
require_python311

if [ "$SELECTED" = UNINSTALL ]; then
    if ! confirm_uninstall; then
        printf '%s\n' "Uninstall cancelled."
        exit 0
    fi
    if installed_uninstaller=$(find_installed_uninstaller); then
        heading "Uninstalling Adaptive Master-Subagent Orchestration"
        run_package_operation "$installed_uninstaller" UNINSTALL
        printf '\n%s\n' "Uninstall completed successfully. Restart Codex to refresh discovered plugins and agents."
        exit 0
    fi
fi

TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/ams-install.XXXXXX")
safe_ref=$(printf '%s' "$REF" | tr '/\\' '--')
archive_path="$TEMP_ROOT/adaptive-master-subagent-orchestration-${safe_ref}.zip"
extract_path="$TEMP_ROOT/extracted"
prepare_archive "$archive_path"
safe_extract "$archive_path" "$extract_path"

case "$SELECTED" in
    A) option_dir="adaptive-master-subagent-orchestration-option-a-two-skill" ;;
    B) option_dir="adaptive-master-subagent-orchestration-option-b-unified" ;;
    C|UNINSTALL) option_dir="adaptive-master-subagent-orchestration-option-c-installer-required" ;;
esac
package_root=$(find_package_root "$extract_path" "$option_dir")
installer="$package_root/scripts/install_package.py"
[ -f "$installer" ] && [ ! -L "$installer" ] || fail "Selected package installer was not found: $installer"

if [ "$SELECTED" = UNINSTALL ]; then
    heading "Uninstalling Adaptive Master-Subagent Orchestration"
else
    heading "Installing Option $SELECTED"
fi
run_package_operation "$installer" "$SELECTED"

if [ "$SELECTED" = UNINSTALL ]; then
    printf '\n%s\n' "Uninstall completed successfully. Restart Codex to refresh discovered plugins and agents."
else
    printf '\nOption %s installed successfully. Restart Codex if it does not appear immediately.\n' "$SELECTED"
fi
