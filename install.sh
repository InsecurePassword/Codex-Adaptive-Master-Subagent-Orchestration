#!/bin/sh
# Adaptive Master-Subagent Orchestration remote installer
# Version 3.1.0

set -eu

REPOSITORY="InsecurePassword/adaptive-master-subagent-orchestration"
REF="main"
RELEASE_VERSION="3.1.0"
ARCHIVE_NAME="adaptive-master-subagent-orchestration-${REF}.zip"
PUBLIC_ARCHIVE_URL="https://github.com/${REPOSITORY}/archive/refs/heads/${REF}.zip"
PRIVATE_ARCHIVE_URL="https://api.github.com/repos/${REPOSITORY}/zipball/${REF}"
MANAGED_MARKER="# managed-by: adaptive-master-subagent-orchestration"

PLUGIN_NAMES="
adaptive-master-subagent-orchestration-option-a-two-skill
adaptive-master-subagent-orchestration-option-b-unified
adaptive-master-subagent-orchestration-option-c-installer-required
adaptive-master-subagent-orchestration-option-a-modular
adaptive-master-subagent-orchestration-option-c-lean
adaptive-master-subagent-orchestration
"

TEMP_ROOT=""
cleanup() {
    if [ -n "$TEMP_ROOT" ] && [ -d "$TEMP_ROOT" ]; then
        rm -rf "$TEMP_ROOT"
    fi
}
trap cleanup EXIT HUP INT TERM

heading() {
    printf '\n%s\n' "$1"
    printf '%s\n' "$1" | sed 's/./=/g'
}

normalize_option() {
    value=$(printf '%s' "$1" | tr '[:lower:]' '[:upper:]')
    case "$value" in
        1|A) printf '%s\n' "A" ;;
        2|B) printf '%s\n' "B" ;;
        3|C) printf '%s\n' "C" ;;
        4|UNINSTALL|REMOVE) printf '%s\n' "UNINSTALL" ;;
        *) printf 'Unsupported selection: %s\n' "$1" >&2; return 1 ;;
    esac
}

prompt_selection() {
    if [ ! -r /dev/tty ]; then
        printf '%s\n' "Interactive input is unavailable. Set AMS_INSTALL_OPTION=A, B, C, or UNINSTALL." >&2
        return 1
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
    [ -n "$choice" ] || choice="1"
    normalize_option "$choice"
}

codex_home() {
    if [ -n "${CODEX_HOME:-}" ]; then
        printf '%s\n' "$CODEX_HOME"
    else
        printf '%s\n' "$HOME/.codex"
    fi
}

is_plugin_name() {
    candidate=$1
    case "$candidate" in
        adaptive-master-subagent-orchestration-option-a-two-skill|adaptive-master-subagent-orchestration-option-a-two-skill.backup-*|adaptive-master-subagent-orchestration-option-a-two-skill.installing-*|\
        adaptive-master-subagent-orchestration-option-b-unified|adaptive-master-subagent-orchestration-option-b-unified.backup-*|adaptive-master-subagent-orchestration-option-b-unified.installing-*|\
        adaptive-master-subagent-orchestration-option-c-installer-required|adaptive-master-subagent-orchestration-option-c-installer-required.backup-*|adaptive-master-subagent-orchestration-option-c-installer-required.installing-*|\
        adaptive-master-subagent-orchestration-option-a-modular|adaptive-master-subagent-orchestration-option-a-modular.backup-*|adaptive-master-subagent-orchestration-option-a-modular.installing-*|\
        adaptive-master-subagent-orchestration-option-c-lean|adaptive-master-subagent-orchestration-option-c-lean.backup-*|adaptive-master-subagent-orchestration-option-c-lean.installing-*|\
        adaptive-master-subagent-orchestration|adaptive-master-subagent-orchestration.backup-*|adaptive-master-subagent-orchestration.installing-*) return 0 ;;
        *) return 1 ;;
    esac
}

confirm_uninstall() {
    if [ "${AMS_UNINSTALL_FORCE:-0}" = "1" ]; then
        return 0
    fi
    if [ ! -r /dev/tty ]; then
        printf '%s\n' "Uninstall requires confirmation. Set AMS_UNINSTALL_FORCE=1 for non-interactive removal." >&2
        return 1
    fi
    cat >/dev/tty <<'NOTICE'
This removes package-managed plugins, managed agent profiles, legacy skill directories,
and the user-level AMS configuration. Project-local .codex configuration files and
unrelated user files will not be removed.
NOTICE
    printf '%s' "Type REMOVE to continue: " >/dev/tty
    IFS= read -r confirmation </dev/tty || confirmation=""
    [ "$confirmation" = "REMOVE" ]
}

uninstall_ams() {
    heading "Uninstalling Adaptive Master-Subagent Orchestration"
    if ! confirm_uninstall; then
        printf '%s\n' "Uninstall cancelled."
        return 0
    fi

    market_root="$HOME/.agents/plugins"
    plugin_root="$market_root/plugins"
    marketplace="$market_root/marketplace.json"
    codex_dir=$(codex_home)
    agents_dir="$codex_dir/agents"
    config_path="$codex_dir/ams-orchestration.toml"

    if [ -d "$plugin_root" ]; then
        for path in "$plugin_root"/*; do
            [ -d "$path" ] || continue
            name=$(basename "$path")
            if is_plugin_name "$name"; then
                rm -rf "$path"
                printf 'removed plugin directory: %s\n' "$path"
            fi
        done
    fi

    if [ -f "$marketplace" ]; then
        command -v python3 >/dev/null 2>&1 || {
            printf '%s\n' "python3 is required to safely update marketplace.json during uninstall." >&2
            return 1
        }
        AMS_MARKETPLACE_PATH="$marketplace" AMS_PLUGIN_NAMES="$PLUGIN_NAMES" python3 <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["AMS_MARKETPLACE_PATH"])
names = {line.strip() for line in os.environ["AMS_PLUGIN_NAMES"].splitlines() if line.strip()}
data = json.loads(path.read_text(encoding="utf-8"))
plugins = data.get("plugins")
if isinstance(plugins, list):
    data["plugins"] = [item for item in plugins if not (isinstance(item, dict) and item.get("name") in names)]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
        printf 'updated marketplace registration: %s\n' "$marketplace"
    fi

    if [ -d "$agents_dir" ]; then
        for path in "$agents_dir"/ams_*; do
            [ -f "$path" ] || continue
            if grep -Fq "$MANAGED_MARKER" "$path" 2>/dev/null; then
                rm -f "$path"
                printf 'removed managed profile: %s\n' "$path"
            fi
        done
    fi

    if [ -f "$config_path" ]; then
        rm -f "$config_path"
        printf 'removed user configuration: %s\n' "$config_path"
    fi

    legacy_skill_root="$HOME/.agents/skills"
    for legacy_name in adaptive-master-subagent-orchestration ams-orchestration ams-installer; do
        legacy_path="$legacy_skill_root/$legacy_name"
        if [ -d "$legacy_path" ]; then
            rm -rf "$legacy_path"
            printf 'removed legacy skill directory: %s\n' "$legacy_path"
        fi
    done

    printf '\n%s\n' "Uninstall complete. Restart Codex to refresh discovered plugins and agents."
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        printf 'Required command not found: %s\n' "$1" >&2
        return 1
    }
}

require_python311() {
    require_command python3
    python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' || {
        printf '%s\n' "Python 3.11 or later is required." >&2
        return 1
    }
}

verify_package_manifest() {
    package_root=$1
    manifest="$package_root/MANIFEST.sha256"
    [ -f "$manifest" ] || {
        printf 'Package manifest was not found: %s\n' "$manifest" >&2
        return 1
    }
    require_command sha256sum
    (cd "$package_root" && sha256sum -c MANIFEST.sha256 >/dev/null)
    printf '%s\n' "Selected package manifest verified."
}

download_archive() {
    destination=$1
    require_command curl
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        curl -fsSL --retry 3 --retry-delay 1 \
            -H "Authorization: Bearer $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github+json" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "$PRIVATE_ARCHIVE_URL" -o "$destination"
    else
        if ! curl -fsSL --retry 3 --retry-delay 1 "$PUBLIC_ARCHIVE_URL" -o "$destination"; then
            printf '%s\n' "Repository package download failed. The repository is private; set GITHUB_TOKEN to a token with repository read access and retry." >&2
            return 1
        fi
    fi
}

install_option() {
    selected=$1
    require_python311
    require_command unzip

    case "$selected" in
        A) option_dir="adaptive-master-subagent-orchestration-option-a-two-skill" ;;
        B) option_dir="adaptive-master-subagent-orchestration-option-b-unified" ;;
        C) option_dir="adaptive-master-subagent-orchestration-option-c-installer-required" ;;
        *) printf 'Internal error: unsupported option %s\n' "$selected" >&2; return 1 ;;
    esac

    TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/ams-install.XXXXXX")
    archive_path="$TEMP_ROOT/$ARCHIVE_NAME"
    extract_path="$TEMP_ROOT/extracted"
    mkdir -p "$extract_path"

    if [ -n "${GITHUB_TOKEN:-}" ]; then
        download_url=$PRIVATE_ARCHIVE_URL
    else
        download_url=$PUBLIC_ARCHIVE_URL
    fi
    printf 'Downloading repository package: %s\n' "$download_url"
    download_archive "$archive_path"
    unzip -q "$archive_path" -d "$extract_path"

    package_root=$(find "$extract_path" -type d -name "$option_dir" -print | head -n 1)
    [ -n "$package_root" ] || {
        printf 'Selected package directory was not found after extraction: %s\n' "$option_dir" >&2
        return 1
    }
    verify_package_manifest "$package_root"
    installer="$package_root/scripts/install_package.py"
    [ -f "$installer" ] || {
        printf 'Selected package installer was not found: %s\n' "$installer" >&2
        return 1
    }

    intensity=${AMS_INTENSITY:-auto}
    spark_efforts=${AMS_SPARK_EFFORTS:-low,medium,high}

    heading "Installing Option $selected"
    if [ "${AMS_EXCLUDE_SPARK:-0}" = "1" ]; then
        python3 "$installer" --home "$HOME" --upgrade-managed --intensity "$intensity" --spark-efforts "$spark_efforts" --exclude-spark
    else
        python3 "$installer" --home "$HOME" --upgrade-managed --intensity "$intensity" --spark-efforts "$spark_efforts"
    fi

    codex_dir=$(codex_home)
    config_path="$codex_dir/ams-orchestration.toml"
    if [ -f "$config_path" ] && grep -Fq '\n' "$config_path" 2>/dev/null; then
        AMS_CONFIG_PATH="$config_path" python3 <<'PYCFG'
import os
from pathlib import Path
path = Path(os.environ["AMS_CONFIG_PATH"])
text = path.read_text(encoding="utf-8")
path.write_text(text.replace("\\n", "\n"), encoding="utf-8")
PYCFG
    fi

    printf '\nOption %s installed successfully. Restart Codex if it does not appear immediately.\n' "$selected"
}

selection=${AMS_INSTALL_OPTION:-${1:-}}
if [ -n "$selection" ]; then
    selection=$(normalize_option "$selection")
else
    selection=$(prompt_selection)
fi

case "$selection" in
    UNINSTALL) uninstall_ams ;;
    A|B|C) install_option "$selection" ;;
    *) printf 'Internal error: unsupported selection %s\n' "$selection" >&2; exit 1 ;;
esac
