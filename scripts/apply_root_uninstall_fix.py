#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected one match in {path}, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


powershell = ROOT / "install.ps1"
old_ps_function = '''function Get-InstalledUninstaller {
    $PluginRoot = Join-Path $HomeDirectory ".agents\\plugins\\plugins"
    if (-not (Test-Path -LiteralPath $PluginRoot -PathType Container)) { return $null }
    $Names = @(
        "adaptive-master-subagent-orchestration-option-a-two-skill",
        "adaptive-master-subagent-orchestration-option-b-unified",
        "adaptive-master-subagent-orchestration-option-c-installer-required",
        "adaptive-master-subagent-orchestration-option-a-modular",
        "adaptive-master-subagent-orchestration-option-c-lean",
        "adaptive-master-subagent-orchestration"
    )
    foreach ($Name in $Names) {
        $Candidate = Join-Path (Join-Path $PluginRoot $Name) "scripts\\install_package.py"
        if (Test-Path -LiteralPath $Candidate -PathType Leaf) { return $Candidate }
    }
    return $null
}
'''
new_ps_function = '''function Get-InstalledUninstaller {
    param([Parameter(Mandatory = $true)]$Python)
    $Finder = @'
from pathlib import Path
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
plugin_root = home / ".agents" / "plugins" / "plugins"
for name in names:
    candidate = plugin_root / name / "scripts" / "install_package.py"
    if candidate.is_file() and not candidate.is_symlink():
        print(candidate)
        raise SystemExit(0)
backup_root = home / ".agents" / "plugins" / "backups"
for name in names:
    for backup in sorted(backup_root.glob(f"{name}.backup-*"), reverse=True):
        candidate = backup / "scripts" / "install_package.py"
        if candidate.is_file() and not candidate.is_symlink():
            print(candidate)
            raise SystemExit(0)
raise SystemExit(3)
'@
    $Output = & $Python.Executable @($Python.Prefix + @("-B", "-E", "-s", "-S", "-c", $Finder, $HomeDirectory))
    $Code = $LASTEXITCODE
    if ($Code -eq 0) {
        $Candidate = [string]($Output | Select-Object -Last 1)
        if ([string]::IsNullOrWhiteSpace($Candidate)) {
            throw "Installed AMS uninstaller discovery returned an empty path."
        }
        return $Candidate.Trim()
    }
    if ($Code -eq 3) { return $null }
    throw "Installed AMS uninstaller discovery failed with exit code $Code."
}
'''
replace_once(powershell, old_ps_function, new_ps_function)
replace_once(
    powershell,
    '''        $InstalledUninstaller = Get-InstalledUninstaller
        if (-not [string]::IsNullOrWhiteSpace($InstalledUninstaller)) {
            Write-Heading "Uninstalling Adaptive Master-Subagent Orchestration"
            Invoke-ResolvedPython -Python $Python -Arguments @($InstalledUninstaller, "--home", $HomeDirectory, "--uninstall", "--yes")
            Write-Host ""
            Write-Host "Uninstall completed successfully. Restart Codex to refresh discovered plugins and agents." -ForegroundColor Green
            exit 0
        }
''',
    '''        $InstalledUninstaller = Get-InstalledUninstaller -Python $Python
        if (-not [string]::IsNullOrWhiteSpace($InstalledUninstaller)) {
            Write-Heading "Uninstalling Adaptive Master-Subagent Orchestration"
            Invoke-ResolvedPython -Python $Python -Arguments @($InstalledUninstaller, "--home", $HomeDirectory, "--uninstall", "--yes")
            Write-Host ""
            Write-Host "Uninstall completed successfully. Restart Codex to refresh discovered plugins and agents." -ForegroundColor Green
            exit 0
        }
        Write-Host "No package-managed AMS installation was found."
        exit 0
''',
)

shell = ROOT / "install.sh"
old_sh_function = '''find_installed_uninstaller() {
    plugin_root="$INSTALL_HOME/.agents/plugins/plugins"
    [ -d "$plugin_root" ] || return 1
    for name in \\
        adaptive-master-subagent-orchestration-option-a-two-skill \\
        adaptive-master-subagent-orchestration-option-b-unified \\
        adaptive-master-subagent-orchestration-option-c-installer-required \\
        adaptive-master-subagent-orchestration-option-a-modular \\
        adaptive-master-subagent-orchestration-option-c-lean \\
        adaptive-master-subagent-orchestration
    do
        candidate="$plugin_root/$name/scripts/install_package.py"
        if [ -f "$candidate" ] && [ ! -L "$candidate" ]; then
            printf '%s\\n' "$candidate"
            return 0
        fi
    done
    return 1
}
'''
new_sh_function = '''find_installed_uninstaller() {
    python3 -I -S - "$INSTALL_HOME" <<'PY'
from pathlib import Path
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
plugin_root = home / ".agents" / "plugins" / "plugins"
for name in names:
    candidate = plugin_root / name / "scripts" / "install_package.py"
    if candidate.is_file() and not candidate.is_symlink():
        print(candidate)
        raise SystemExit(0)
backup_root = home / ".agents" / "plugins" / "backups"
for name in names:
    for backup in sorted(backup_root.glob(f"{name}.backup-*"), reverse=True):
        candidate = backup / "scripts" / "install_package.py"
        if candidate.is_file() and not candidate.is_symlink():
            print(candidate)
            raise SystemExit(0)
raise SystemExit(1)
PY
}
'''
replace_once(shell, old_sh_function, new_sh_function)
replace_once(
    shell,
    '''    if installed_uninstaller=$(find_installed_uninstaller); then
        heading "Uninstalling Adaptive Master-Subagent Orchestration"
        run_package_operation "$installed_uninstaller" UNINSTALL
        printf '\\n%s\\n' "Uninstall completed successfully. Restart Codex to refresh discovered plugins and agents."
        exit 0
    fi
fi
''',
    '''    if installed_uninstaller=$(find_installed_uninstaller); then
        heading "Uninstalling Adaptive Master-Subagent Orchestration"
        run_package_operation "$installed_uninstaller" UNINSTALL
        printf '\\n%s\\n' "Uninstall completed successfully. Restart Codex to refresh discovered plugins and agents."
        exit 0
    fi
    printf '%s\\n' "No package-managed AMS installation was found."
    exit 0
fi
''',
)

test = ROOT / "tests" / "test_installers.py"
replace_once(
    test,
    '''        require(not curl_marker.exists(), "offline uninstall attempted a download")
        require(active_plugins(home) == [], "offline uninstall left an active option")
        require((unrelated / "keep.txt").exists(), "offline uninstall removed unrelated plugin")
''',
    '''        require(not curl_marker.exists(), "offline uninstall attempted a download")
        require(active_plugins(home) == [], "offline uninstall left an active option")
        require((unrelated / "keep.txt").exists(), "offline uninstall removed unrelated plugin")
        second = run(
            [shell, str(ROOT / "install.sh"), "--option", "UNINSTALL", "--home", str(home), "--force"],
            env=offline_env,
        )
        require("No package-managed AMS installation was found" in second, "repeated root uninstall was not a local no-op")
        require(not curl_marker.exists(), "repeated root uninstall attempted a download")
''',
)

print("Root uninstall discovery and idempotence fixed.")
