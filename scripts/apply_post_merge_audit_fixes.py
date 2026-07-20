#!/usr/bin/env python3
"""Apply post-merge installer ownership, test, and documentation fixes."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = (
    "adaptive-master-subagent-orchestration-option-a-two-skill",
    "adaptive-master-subagent-orchestration-option-b-unified",
    "adaptive-master-subagent-orchestration-option-c-installer-required",
)


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0 and new in text:
        return
    if count != 1:
        raise RuntimeError(f"Expected one match in {path}, found {count}: {old[:80]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


def append_before(path: Path, marker: str, addition: str) -> None:
    text = path.read_text(encoding="utf-8")
    if addition.strip() in text:
        return
    if text.count(marker) != 1:
        raise RuntimeError(f"Expected one insertion marker in {path}: {marker!r}")
    path.write_text(text.replace(marker, addition + marker), encoding="utf-8", newline="\n")


def regenerate_manifest(package: Path) -> None:
    lines: list[str] = []
    for path in sorted(package.rglob("*")):
        if not path.is_file() or path.name == "MANIFEST.sha256":
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            raise RuntimeError(f"Generated Python artifact in package: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(package).as_posix()}")
    (package / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


for package_name in PACKAGES:
    package = ROOT / package_name
    installer = package / "scripts" / "install_package.py"
    replace_once(
        installer,
        'return ConfigPlan("create", f\'schema_version = 1\\nintensity = "{initial_intensity}"\\n\')',
        'return ConfigPlan("create", f\'{MANAGED_MARKER}\\nschema_version = 1\\nintensity = "{initial_intensity}"\\n\')',
    )
    replace_once(
        installer,
        '        normalized = raw.replace("\\\\n", "\\n")\n        validate_config_text(normalized, path)\n        return ConfigPlan("repair-legacy-newlines", normalized)',
        '        normalized = raw.replace("\\\\n", "\\n")\n        if MANAGED_MARKER not in normalized:\n            normalized = f"{MANAGED_MARKER}\\n{normalized}"\n        validate_config_text(normalized, path)\n        return ConfigPlan("repair-legacy-newlines", normalized)',
    )
    replace_once(
        installer,
        '    config = codex_home / "ams-orchestration.toml"\n    if config.exists() or config.is_symlink():\n        targets.append(config)\n    if codex_home.is_dir():\n        targets.extend(codex_home.glob(".ams-orchestration.toml.ams-uninstalling-*"))',
        '    config = codex_home / "ams-orchestration.toml"\n    if path_has_managed_marker(config):\n        targets.append(config)\n    if codex_home.is_dir():\n        targets.extend(\n            path\n            for path in codex_home.glob(".ams-orchestration.toml.ams-uninstalling-*")\n            if path_has_managed_marker(path)\n        )',
    )

    intensity = package / "scripts" / "set_intensity.py"
    replace_once(
        intensity,
        'VALID = ("auto", "minimal", "moderate", "heavy", "extreme")\nLOCK_STALE_SECONDS',
        'VALID = ("auto", "minimal", "moderate", "heavy", "extreme")\nMANAGED_MARKER = "# managed-by: adaptive-master-subagent-orchestration"\nLOCK_STALE_SECONDS',
    )
    replace_once(
        intensity,
        '    text = f\'schema_version = 1\\nintensity = "{args.mode}"\\n\'',
        '    text = f\'{MANAGED_MARKER}\\nschema_version = 1\\nintensity = "{args.mode}"\\n\'',
    )

    test = package / "scripts" / "test_installation.py"
    replace_once(
        test,
        "        config=tomllib.loads((home/'.codex/ams-orchestration.toml').read_text(encoding='utf-8')); require(config['intensity']=='heavy','intensity not written')",
        "        config_path=home/'.codex/ams-orchestration.toml'\n        config_text=config_path.read_text(encoding='utf-8')\n        config=tomllib.loads(config_text); require(config['intensity']=='heavy','intensity not written')\n        require(MANAGED in config_text,'new user config was not marked as package-managed')",
    )
    append_before(
        test,
        "        malformed=base/'malformed';",
        "        user_config_home=base/'user-config'; (user_config_home/'.codex').mkdir(parents=True)\n        user_config=user_config_home/'.codex/ams-orchestration.toml'\n        user_config_text='schema_version = 1\\nintensity = \"moderate\"\\n'\n        user_config.write_text(user_config_text,encoding='utf-8')\n        run(user_config_home,'--exclude-spark','--upgrade-managed')\n        require(user_config.read_text(encoding='utf-8')==user_config_text,'install changed a pre-existing user config')\n        run(user_config_home,'--uninstall','--yes')\n        require(user_config.read_text(encoding='utf-8')==user_config_text,'uninstall removed a pre-existing user config')\n\n",
    )
    replace_once(
        test,
        "        require(not list((home/'.codex/agents').glob('ams_*.toml')),'uninstall left managed profiles')\n        run(home,'--uninstall','--yes')",
        "        require(not list((home/'.codex/agents').glob('ams_*.toml')),'uninstall left managed profiles')\n        require(not config_path.exists(),'uninstall left a package-managed user config')\n        run(home,'--uninstall','--yes')",
    )

root_test = ROOT / "tests" / "test_installers.py"
append_before(
    root_test,
    "def test_process_tree_timeout(base: Path) -> None:\n",
    '''def require_install_layout(home: Path, codex_home: Path, option: str) -> None:\n    plugin = home / ".agents" / "plugins" / "plugins" / PACKAGE_NAMES[option]\n    require((plugin / ".codex-plugin" / "plugin.json").is_file(), f"Option {option} plugin metadata is misplaced")\n    require((plugin / "scripts" / "install_package.py").is_file(), f"Option {option} installer is missing from installed plugin")\n    require((home / ".agents" / "plugins" / "marketplace.json").is_file(), "marketplace file is misplaced")\n    require((codex_home / "agents").is_dir(), "managed profiles directory is misplaced")\n    require((codex_home / "ams-orchestration.toml").is_file(), "user configuration is misplaced")\n\n\n''',
)
replace_once(
    root_test,
    '    require(active_plugins(home) == [PACKAGE_NAMES["A"]], "PowerShell install selected the wrong option")\n    run(\n        [\n            executable,\n            "-NoProfile",\n            "-File",\n            str(ROOT / "install.ps1"),\n            "-Option",\n            "Uninstall",\n            "-HomeDirectory",\n            str(home),\n            "-Force",\n        ]\n    )\n    require(active_plugins(home) == [], "PowerShell uninstall left an active plugin")',
    '''    require(active_plugins(home) == [PACKAGE_NAMES["A"]], "PowerShell install selected the wrong option")\n    require_install_layout(home, home / ".codex", "A")\n    run([executable, "-NoProfile", "-File", str(ROOT / "install.ps1"), "-Option", "B", "-ArchivePath", str(archive), "-HomeDirectory", str(home)])\n    require(active_plugins(home) == [PACKAGE_NAMES["B"]], "PowerShell option switch left multiple active plugins")\n    require_install_layout(home, home / ".codex", "B")\n    c_home = base / "powershell-c-home"\n    run([executable, "-NoProfile", "-File", str(ROOT / "install.ps1"), "-Option", "C", "-ArchivePath", str(archive), "-HomeDirectory", str(c_home), "-ExcludeSpark"])\n    require(active_plugins(c_home) == [PACKAGE_NAMES["C"]], "PowerShell Option C installed the wrong plugin")\n    require_install_layout(c_home, c_home / ".codex", "C")\n    for uninstall_home in (home, c_home):\n        run([executable, "-NoProfile", "-File", str(ROOT / "install.ps1"), "-Option", "Uninstall", "-HomeDirectory", str(uninstall_home), "-Force"])\n        require(active_plugins(uninstall_home) == [], "PowerShell uninstall left an active plugin")''',
)
replace_once(
    root_test,
    '        require(len(list((home / ".codex" / "agents").glob("*.toml"))) == 15, "exclude-spark was ignored")',
    '        require(len(list((home / ".codex" / "agents").glob("*.toml"))) == 15, "exclude-spark was ignored")\n        require_install_layout(home, home / ".codex", "A")',
)
append_before(
    root_test,
    '        print("[root-test] offline uninstall using installed package", flush=True)\n',
    '''        print("[root-test] custom CODEX_HOME placement", flush=True)\n        custom_home = base / "custom-home"\n        custom_codex = base / "custom-codex"\n        custom_env = dict(os.environ)\n        custom_env["CODEX_HOME"] = str(custom_codex)\n        run([shell, str(ROOT / "install.sh"), "--option", "A", "--archive-path", str(archive), "--home", str(custom_home), "--exclude-spark"], env=custom_env)\n        require_install_layout(custom_home, custom_codex, "A")\n        require(not (custom_home / ".codex").exists(), "custom CODEX_HOME install also wrote to the default home")\n        project_config = custom_home / "project" / ".codex" / "ams-orchestration.toml"\n        project_config.parent.mkdir(parents=True)\n        project_config.write_text('schema_version = 1\\nintensity = "minimal"\\n', encoding="utf-8")\n        run([shell, str(ROOT / "install.sh"), "--option", "UNINSTALL", "--home", str(custom_home), "--force"], env=custom_env)\n        require(not custom_codex.joinpath("ams-orchestration.toml").exists(), "custom CODEX_HOME uninstall left managed config")\n        require(project_config.exists(), "uninstall removed project-local configuration")\n\n''',
)

readme = ROOT / "README.md"
replace_once(readme, "The installer asks which package to install. Press **Enter** to choose. **Option A** is the recommended package for most users, while **Option B** is the simplest and requires the least amount of configuration. Menu option **4** removes package-managed files.", "The installer asks which package to install. Press **Enter** without typing a selection to install **Option A**, the recommended package for most users. **Option B** is the simplest single-skill package. Menu option **4** removes package-managed files.")
replace_once(readme, "| **A-Recommended** |", "| **A — Recommended** |")
replace_once(readme, "| **B-Unified** |", "| **B — Unified** |")
replace_once(readme, "| **C-Lean runtime** |", "| **C — Lean runtime** |")

usage = ROOT / "INSTALLER-USAGE.md"
replace_once(usage, "- the user-level `ams-orchestration.toml`", "- the user-level `ams-orchestration.toml` when it carries the package-managed marker")
replace_once(usage, "Unrelated files and project-level `.codex` configuration remain unchanged.", "Pre-existing unmarked user configuration, unrelated files, and project-level `.codex` configuration remain unchanged.")
replace_once(usage, "The audit checks shell and Python syntax, PowerShell syntax when a PowerShell runtime is available, root installer integration, every package installer, rollback, locking, option switching, archive validation, uninstall, and package manifests.", "The audit checks shell and Python syntax, native PowerShell execution on Windows CI, root installer integration, every package installer, installation paths, rollback, locking, option switching, archive validation, uninstall ownership, package manifests, and every Markdown file and local link.")

manual = ROOT / "MANUAL-INSTALLATION.md"
replace_once(manual, "|   |-- audit_installers.py\n|   `-- process_utils.py", "|   |-- audit_installers.py\n|   |-- audit_markdown.py\n|   `-- process_utils.py")
replace_once(manual, "The uninstall path removes package-managed files while preserving unrelated profiles, marketplace entries, plugins, and project-level `.codex` configuration.", "The uninstall path removes package-managed files while preserving pre-existing unmarked user configuration, unrelated profiles, marketplace entries, plugins, and project-level `.codex` configuration.")

installer_audit = ROOT / "INSTALLER-AUDIT.md"
replace_once(installer_audit, "- generated-artifact checks", "- generated-artifact checks\n- repository-wide Markdown structure, readability, and local-link checks\n- native Windows PowerShell installation, option switching, path-placement, and uninstall checks")
replace_once(installer_audit, "The full Python and POSIX integration matrix is executable on Linux. Windows-specific PowerShell behavior is executed when `powershell.exe` or `pwsh` is available; otherwise the audit performs static PowerShell checks. A native Windows release check remains appropriate whenever a Windows runtime is explicitly required.", "The release workflow runs the complete audit on both Ubuntu and Windows. Windows CI executes the PowerShell installer for Options A, B, and C, verifies package switching and file placement, and runs uninstall. Local systems without PowerShell still receive static PowerShell checks.")

audit = ROOT / "scripts" / "audit_installers.py"
append_before(
    audit,
    "def root_integration_tests() -> None:\n",
    '''def markdown_audit() -> None:\n    print("[audit] Markdown structure and links")\n    run([sys.executable, "-B", "-E", "-s", "-S", str(ROOT / "scripts" / "audit_markdown.py")], timeout=60)\n\n\n''',
)
replace_once(audit, "    no_generated_artifacts()\n    if not args.skip_root_tests:", "    no_generated_artifacts()\n    markdown_audit()\n    if not args.skip_root_tests:")

for package_name in PACKAGES:
    regenerate_manifest(ROOT / package_name)

print("Post-merge audit fixes applied.")
