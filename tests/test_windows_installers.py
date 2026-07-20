#!/usr/bin/env python3
"""Independent native-Windows lifecycle audit for AMS PowerShell installers."""
from __future__ import annotations

import contextlib
import importlib.util
import json
import os
import shutil
import socket
import stat
import struct
import subprocess
import sys
import tempfile
import time
import tomllib
import warnings
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import process_utils as process_utils_module  # noqa: E402
from process_utils import process_is_alive, run_bounded  # noqa: E402

TIMEOUT = 180
MANAGED = "# managed-by: adaptive-master-subagent-orchestration"
PACKAGE_NAMES = {
    "A": "adaptive-master-subagent-orchestration-option-a-two-skill",
    "B": "adaptive-master-subagent-orchestration-option-b-unified",
    "C": "adaptive-master-subagent-orchestration-option-c-installer-required",
}
EXPECTED_SKILLS = {
    "A": {"ams-installer", "ams-orchestration"},
    "B": {"adaptive-master-subagent-orchestration"},
    "C": {"ams-orchestration"},
}
ALL_NAMES = set(PACKAGE_NAMES.values()) | {
    "adaptive-master-subagent-orchestration-option-a-modular",
    "adaptive-master-subagent-orchestration-option-c-lean",
    "adaptive-master-subagent-orchestration",
}
TEXT_SUFFIXES = {".ps1", ".py", ".sh", ".md", ".toml", ".json", ".yaml", ".yml", ".sha256"}
TEXT_NAMES = {"VERSION", "PACKAGE-OPTION", ".gitattributes"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    expect: int = 0,
    timeout: int | float = TIMEOUT,
    stdin_text: str | None = None,
) -> str:
    stdin_handle = None
    try:
        if stdin_text is not None:
            stdin_handle = tempfile.TemporaryFile(mode="w+t", encoding="utf-8", newline="\n")
            stdin_handle.write(stdin_text)
            stdin_handle.seek(0)
        result = run_bounded(
            command,
            timeout=timeout,
            text=True,
            capture_output=True,
            check=False,
            env=env,
            cwd=cwd,
            stdin=stdin_handle if stdin_handle is not None else subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as exc:
        raise AssertionError(f"command timed out after {timeout}s: {command}") from exc
    finally:
        if stdin_handle is not None:
            stdin_handle.close()
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != expect:
        raise AssertionError(
            f"command returned {result.returncode}, expected {expect}: {command}\n{output}"
        )
    return output


def powershell_runtimes() -> list[tuple[str, str]]:
    candidates = [
        ("Windows PowerShell 5.1", shutil.which("powershell.exe") or shutil.which("powershell")),
        ("PowerShell 7", shutil.which("pwsh.exe") or shutil.which("pwsh")),
    ]
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for label, executable in candidates:
        if not executable:
            continue
        normalized = os.path.normcase(os.path.abspath(executable))
        if normalized in seen:
            continue
        seen.add(normalized)
        found.append((label, executable))
    labels = {label for label, _ in found}
    require("Windows PowerShell 5.1" in labels, "Windows PowerShell 5.1 was not found")
    require("PowerShell 7" in labels, "PowerShell 7 was not found")
    return found


def package_entries(
    *,
    replacements: dict[str, bytes] | None = None,
    omit: set[str] | None = None,
    extras: dict[str, bytes] | None = None,
    refresh_package: str | None = None,
) -> dict[str, bytes]:
    replacements = replacements or {}
    omit = omit or set()
    extras = extras or {}
    entries: dict[str, bytes] = {"install.ps1": (ROOT / "install.ps1").read_bytes()}
    for option, package_name in PACKAGE_NAMES.items():
        package = ROOT / package_name
        for path in package.rglob("*"):
            if path.is_symlink():
                raise AssertionError(f"test source contains symlink: {path}")
            if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            relative = f"{package_name}/{path.relative_to(package).as_posix()}"
            if relative in omit:
                continue
            entries[relative] = replacements.get(relative, path.read_bytes())
    entries.update(extras)
    if refresh_package:
        manifest_key = f"{refresh_package}/MANIFEST.sha256"
        lines: list[str] = []
        for relative in sorted(entries):
            prefix = f"{refresh_package}/"
            if not relative.startswith(prefix) or relative == manifest_key:
                continue
            digest = __import__("hashlib").sha256(entries[relative]).hexdigest()
            lines.append(f"{digest}  {relative[len(prefix):]}")
        entries[manifest_key] = ("\n".join(lines) + "\n").encode("utf-8")
    return entries


def write_archive(
    destination: Path,
    *,
    entries: dict[str, bytes] | None = None,
    prefixes: tuple[str, ...] = ("adaptive-master-subagent-orchestration-windows-audit",),
) -> None:
    entries = entries or package_entries()
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for prefix in prefixes:
            for relative, data in entries.items():
                archive.writestr(f"{prefix}/{relative}", data)


def build_archive(destination: Path) -> None:
    write_archive(destination)


def active_plugins(home: Path) -> list[str]:
    root = home / ".agents" / "plugins" / "plugins"
    if not root.is_dir():
        return []
    return sorted(path.name for path in root.iterdir() if path.name in ALL_NAMES)


def marketplace_data(home: Path) -> dict[str, object]:
    path = home / ".agents" / "plugins" / "marketplace.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def marketplace_plugins(home: Path) -> list[str]:
    return sorted(
        item["name"]
        for item in marketplace_data(home).get("plugins", [])
        if isinstance(item, dict) and item.get("name") in ALL_NAMES
    )


def managed_profiles(codex_home: Path) -> list[Path]:
    agents = codex_home / "agents"
    if not agents.is_dir():
        return []
    result: list[Path] = []
    for path in agents.glob("*.toml"):
        if path.is_file() and MANAGED in path.read_text(encoding="utf-8", errors="replace"):
            result.append(path)
    return sorted(result)


def generated_artifacts(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [
        path
        for path in root.rglob("*")
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}
    ]


def seed_unrelated(home: Path, codex_home: Path, project_root: Path) -> dict[str, bytes]:
    plugin = home / ".agents" / "plugins" / "plugins" / "unrelated-plugin"
    plugin.mkdir(parents=True, exist_ok=True)
    plugin_file = plugin / "keep.txt"
    plugin_file.write_bytes(b"unrelated plugin bytes\n")

    market = home / ".agents" / "plugins" / "marketplace.json"
    market.parent.mkdir(parents=True, exist_ok=True)
    market.write_text(
        json.dumps(
            {
                "name": "existing-marketplace",
                "interface": {"displayName": "Existing"},
                "plugins": [
                    {
                        "name": "unrelated-plugin",
                        "source": {"source": "local", "path": "./plugins/unrelated-plugin"},
                        "custom": {"preserve": True},
                    }
                ],
                "customRoot": {"preserve": True},
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    unrelated_profile = codex_home / "agents" / "personal-profile.toml"
    unrelated_profile.parent.mkdir(parents=True, exist_ok=True)
    unrelated_profile.write_bytes(b'name = "personal-profile"\nmodel = "custom"\n')

    project_config = project_root / ".codex" / "ams-orchestration.toml"
    project_config.parent.mkdir(parents=True, exist_ok=True)
    project_config.write_bytes(b'schema_version = 1\nintensity = "extreme"\n# project-owned\n')

    return {
        "plugin": plugin_file.read_bytes(),
        "profile": unrelated_profile.read_bytes(),
        "project": project_config.read_bytes(),
    }


def assert_unrelated(home: Path, codex_home: Path, project_root: Path, expected: dict[str, bytes]) -> None:
    require(
        (home / ".agents/plugins/plugins/unrelated-plugin/keep.txt").read_bytes() == expected["plugin"],
        "unrelated plugin changed",
    )
    require(
        (codex_home / "agents/personal-profile.toml").read_bytes() == expected["profile"],
        "unrelated profile changed",
    )
    require(
        (project_root / ".codex/ams-orchestration.toml").read_bytes() == expected["project"],
        "project-local configuration changed",
    )
    unrelated = [
        item
        for item in marketplace_data(home).get("plugins", [])
        if isinstance(item, dict) and item.get("name") == "unrelated-plugin"
    ]
    require(
        unrelated
        == [
            {
                "name": "unrelated-plugin",
                "source": {"source": "local", "path": "./plugins/unrelated-plugin"},
                "custom": {"preserve": True},
            }
        ],
        "unrelated marketplace entry changed",
    )
    require(marketplace_data(home).get("customRoot") == {"preserve": True}, "unrelated marketplace root data changed")


def assert_no_transients(home: Path, codex_home: Path) -> None:
    market_root = home / ".agents" / "plugins"
    if market_root.exists():
        require(not list(market_root.glob(".ams-transaction-*")), "stale transaction directory remains")
        require(not (market_root / ".ams-install.lock").exists(), "stale package lock remains")
        for root_name in ("plugins", "backups"):
            root = market_root / root_name
            if root.is_dir():
                leftovers = [
                    path
                    for path in root.iterdir()
                    if ".ams-uninstalling-" in path.name or ".installing-" in path.name
                ]
                require(not leftovers, f"stale staging paths remain: {leftovers}")
    require(not (codex_home / ".agents.ams-profile-install.lock").exists(), "stale profile lock remains")
    require(not (codex_home / ".ams-orchestration-config.lock").exists(), "stale intensity lock remains")


def assert_installed(
    home: Path,
    codex_home: Path,
    project_root: Path,
    option: str,
    unrelated: dict[str, bytes],
    *,
    profile_count: int = 18,
) -> None:
    package_name = PACKAGE_NAMES[option]
    plugin = home / ".agents" / "plugins" / "plugins" / package_name
    require(active_plugins(home) == [package_name], f"Option {option} is not the only active AMS plugin")
    require(marketplace_plugins(home) == [package_name], f"Option {option} is not the only AMS marketplace entry")
    for relative in (
        ".codex-plugin/plugin.json",
        "MANIFEST.sha256",
        "scripts/install_package.py",
        "scripts/bootstrap_profiles.py",
        "scripts/process_utils.py",
        "skills",
    ):
        require((plugin / relative).exists(), f"Option {option} installed content is missing: {relative}")
    skills = {path.name for path in (plugin / "skills").iterdir() if path.is_dir()}
    require(skills == EXPECTED_SKILLS[option], f"Option {option} installed the wrong skill set: {skills}")
    require(len(managed_profiles(codex_home)) == profile_count, f"Option {option} installed the wrong profile count")
    config = codex_home / "ams-orchestration.toml"
    require(config.is_file(), f"Option {option} user configuration is missing")
    require(MANAGED in config.read_text(encoding="utf-8"), f"Option {option} user configuration is not marked")
    assert_unrelated(home, codex_home, project_root, unrelated)
    assert_no_transients(home, codex_home)
    require(not generated_artifacts(home), "installation generated Python bytecode")


def assert_uninstalled(
    home: Path,
    codex_home: Path,
    project_root: Path,
    unrelated: dict[str, bytes],
) -> None:
    require(active_plugins(home) == [], "uninstall left an active AMS plugin")
    require(marketplace_plugins(home) == [], "uninstall left an AMS marketplace entry")
    require(not managed_profiles(codex_home), "uninstall left managed profiles")
    config = codex_home / "ams-orchestration.toml"
    require(not config.exists() and not config.is_symlink(), "uninstall left a package-managed user config")
    backup_root = home / ".agents/plugins/backups"
    if backup_root.is_dir():
        require(
            not any(any(path.name.startswith(name) for name in ALL_NAMES) for path in backup_root.iterdir()),
            "uninstall left recognized AMS backups",
        )
    assert_unrelated(home, codex_home, project_root, unrelated)
    assert_no_transients(home, codex_home)
    require(not generated_artifacts(home), "uninstall generated Python bytecode")


def assert_backup_recoverable(home: Path, previous_option: str) -> None:
    backup_root = home / ".agents" / "plugins" / "backups"
    package_name = PACKAGE_NAMES[previous_option]
    backups = sorted(backup_root.glob(f"{package_name}.backup-*")) if backup_root.is_dir() else []
    require(backups, f"switching from Option {previous_option} did not preserve a recoverable backup")
    backup = backups[-1]
    require((backup / "MANIFEST.sha256").is_file(), "backup manifest is missing")
    require((backup / "scripts/install_package.py").is_file(), "backup uninstaller is missing")
    run(
        [
            sys.executable,
            "-B",
            "-E",
            "-s",
            "-S",
            str(backup / "scripts/validate_package.py"),
            "--scripts-only",
        ],
        timeout=TIMEOUT,
    )


def ps_command(
    executable: str,
    archive: Path,
    home: Path | str,
    option: str,
    *,
    alias: bool = False,
    include_archive: bool = True,
    include_home: bool = True,
    extra: tuple[str, ...] = (),
) -> list[str]:
    command = [
        executable,
        "-NoLogo",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "install.ps1"),
        "-InstallOption" if alias else "-Option",
        option,
    ]
    if include_archive:
        command += ["-ArchivePath", str(archive)]
    if include_home:
        command += ["-HomeDirectory", str(home)]
    command += list(extra)
    return command


def uninstall_command(executable: str, home: Path | str) -> list[str]:
    return [
        executable,
        "-NoLogo",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "install.ps1"),
        "-Option",
        "Uninstall",
        "-HomeDirectory",
        str(home),
        "-Force",
    ]


def lifecycle_matrix(label: str, executable: str, archive: Path, base: Path) -> None:
    print(f"[windows-test] lifecycle matrix: {label}", flush=True)
    for option in PACKAGE_NAMES:
        root = base / f"{label.replace(' ', '-')}-reinstall-{option}"
        home, codex_home, project = root / "home", root / "codex", root / "project"
        unrelated = seed_unrelated(home, codex_home, project)
        env = dict(os.environ, CODEX_HOME=str(codex_home))
        run(ps_command(executable, archive, home, option), env=env, cwd=project)
        assert_installed(home, codex_home, project, option, unrelated)
        run(ps_command(executable, archive, home, option), env=env, cwd=project)
        assert_installed(home, codex_home, project, option, unrelated)
        run(uninstall_command(executable, home), env=env, cwd=project)
        run(uninstall_command(executable, home), env=env, cwd=project)
        assert_uninstalled(home, codex_home, project, unrelated)

    for source in PACKAGE_NAMES:
        for destination in PACKAGE_NAMES:
            if source == destination:
                continue
            root = base / f"{label.replace(' ', '-')}-switch-{source}-{destination}"
            home, codex_home, project = root / "home", root / "codex", root / "project"
            unrelated = seed_unrelated(home, codex_home, project)
            env = dict(os.environ, CODEX_HOME=str(codex_home))
            run(ps_command(executable, archive, home, source), env=env, cwd=project)
            run(ps_command(executable, archive, home, destination), env=env, cwd=project)
            assert_installed(home, codex_home, project, destination, unrelated)
            assert_backup_recoverable(home, source)
            run(uninstall_command(executable, home), env=env, cwd=project)
            assert_uninstalled(home, codex_home, project, unrelated)

    empty = base / f"{label.replace(' ', '-')}-empty-uninstall"
    run(uninstall_command(executable, empty))
    run(uninstall_command(executable, empty))
    require(not empty.exists(), "empty repeated uninstall mutated the requested home")


def selector_contract(executable: str, archive: Path, base: Path) -> None:
    print("[windows-test] selector, alias, numeric, environment, and interactive contracts", flush=True)

    alias_home = base / "selector-alias"
    run(ps_command(executable, archive, alias_home, "A", alias=True))
    require(active_plugins(alias_home) == [PACKAGE_NAMES["A"]], "-InstallOption alias did not select Option A")
    run(uninstall_command(executable, alias_home))

    numeric_home = base / "selector-numeric"
    for numeric, option in (("1", "A"), ("2", "B"), ("3", "C")):
        run(ps_command(executable, archive, numeric_home, numeric))
        require(active_plugins(numeric_home) == [PACKAGE_NAMES[option]], f"numeric option {numeric} selected the wrong package")
    run(ps_command(executable, archive, numeric_home, "4", include_archive=False, extra=("-Force",)))
    require(active_plugins(numeric_home) == [], "numeric uninstall did not remove AMS")

    env_home = base / "selector-env"
    env = dict(
        os.environ,
        AMS_INSTALL_OPTION="A",
        AMS_ARCHIVE_PATH=str(archive),
        AMS_HOME=str(env_home),
    )
    command = [
        executable,
        "-NoLogo",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "install.ps1"),
    ]
    run(command, env=env)
    require(active_plugins(env_home) == [PACKAGE_NAMES["A"]], "environment selection did not install Option A")
    run(uninstall_command(executable, env_home))

    interactive_home = base / "selector-interactive"
    interactive = [
        executable,
        "-NoLogo",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "install.ps1"),
        "-ArchivePath",
        str(archive),
        "-HomeDirectory",
        str(interactive_home),
    ]
    run(interactive, stdin_text="\n")
    require(active_plugins(interactive_home) == [PACKAGE_NAMES["A"]], "blank interactive selection did not default to Option A")
    run(uninstall_command(executable, interactive_home))

    for name, args, env_changes in (
        ("invalid", ("-Option", "Z"), {}),
        ("duplicate", ("-Option", "A", "-Option", "B"), {}),
        ("contradictory-alias", ("-Option", "A", "-InstallOption", "B"), {}),
        ("invalid-environment", (), {"AMS_INSTALL_OPTION": "Z"}),
    ):
        home = base / f"selector-{name}"
        command = [
            executable,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ROOT / "install.ps1"),
            *args,
            "-ArchivePath",
            str(archive),
            "-HomeDirectory",
            str(home),
        ]
        env = dict(os.environ, **env_changes)
        output = run(command, env=env, expect=1)
        require(output.strip(), f"{name} selection failure did not provide a diagnostic")
        require(not home.exists(), f"{name} selection failure mutated installation state")


def custom_path_contract(executable: str, archive: Path, base: Path) -> None:
    print("[windows-test] custom Windows paths and configuration ownership", flush=True)
    nested = "nested-" + ("x" * 72)
    home = base / "AMS Audit" / "ユーザー Home" / nested
    codex_home = base / "Codex ホーム" / "nested directory"
    project = base / "Project Root" / "サンプル"
    unrelated = seed_unrelated(home, codex_home, project)
    decoy_home = base / "AMS_HOME decoy"
    env = dict(
        os.environ,
        CODEX_HOME=str(codex_home) + os.sep,
        AMS_HOME=str(decoy_home),
        AMS_ARCHIVE_PATH=str(archive),
    )
    home_text = str(home) + os.sep
    command = ps_command(
        executable,
        archive,
        home_text,
        "A",
        include_archive=False,
        extra=("-SparkEfforts", "low,high"),
    )
    run(command, env=env, cwd=project)
    assert_installed(home, codex_home, project, "A", unrelated, profile_count=17)
    require(not decoy_home.exists(), "explicit -HomeDirectory did not override AMS_HOME")
    require(not (home / ".codex").exists(), "custom CODEX_HOME also wrote to the default path")

    config = codex_home / "ams-orchestration.toml"
    require(MANAGED in config.read_text(encoding="utf-8"), "custom CODEX_HOME config is not managed")

    # Re-run through AMS_HOME and AMS_ARCHIVE_PATH without explicit path arguments.
    env_home = base / "環境 Home"
    env2 = dict(os.environ, AMS_HOME=str(env_home), AMS_ARCHIVE_PATH=str(archive), AMS_INSTALL_OPTION="B")
    command2 = [
        executable,
        "-NoLogo",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "install.ps1"),
    ]
    run(command2, env=env2)
    require(active_plugins(env_home) == [PACKAGE_NAMES["B"]], "AMS_HOME or AMS_ARCHIVE_PATH failed")
    run(uninstall_command(executable, env_home), env=env2)

    # Windows paths are case-insensitive; discovery must survive drive-letter casing changes.
    uninstall_home = str(home)
    if len(uninstall_home) >= 2 and uninstall_home[1] == ":":
        uninstall_home = uninstall_home[0].swapcase() + uninstall_home[1:]
    run(uninstall_command(executable, uninstall_home), env=env, cwd=project)
    assert_uninstalled(home, codex_home, project, unrelated)

    pre_home = base / "preexisting-home"
    pre_codex = base / "preexisting-codex"
    pre_project = base / "preexisting-project"
    unrelated2 = seed_unrelated(pre_home, pre_codex, pre_project)
    config2 = pre_codex / "ams-orchestration.toml"
    original = b'schema_version = 1\nintensity = "moderate"\n'
    config2.write_bytes(original)
    env3 = dict(os.environ, CODEX_HOME=str(pre_codex))
    for option in ("A", "B", "C"):
        run(ps_command(executable, archive, pre_home, option), env=env3, cwd=pre_project)
        require(config2.read_bytes() == original, "package switching changed a pre-existing user config")
    run(uninstall_command(executable, pre_home), env=env3, cwd=pre_project)
    require(config2.read_bytes() == original, "uninstall removed a pre-existing user config")
    assert_unrelated(pre_home, pre_codex, pre_project, unrelated2)


def option_c_skip_profiles_contract(executable: str, base: Path) -> None:
    print("[windows-test] Option C mandatory profiles", flush=True)
    package = ROOT / PACKAGE_NAMES["C"]
    home = base / "option-c-skip"
    output = run(
        [
            executable,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(package / "Install-Package.ps1"),
            "-HomeDirectory",
            str(home),
            "-SkipProfiles",
        ],
        expect=1,
    )
    require("requires profile installation" in output.lower(), "Option C PowerShell wrapper did not reject -SkipProfiles")
    require(not home.exists(), "Option C -SkipProfiles failure mutated the home")
    output = run(
        [
            sys.executable,
            "-B",
            "-E",
            "-s",
            "-S",
            str(package / "scripts/install_package.py"),
            "--home",
            str(home),
            "--skip-profiles",
        ],
        expect=1,
    )
    require("requires profile installation" in output.lower(), "Option C Python installer did not reject --skip-profiles")


def wrappers_contract(executable: str, base: Path) -> None:
    print("[windows-test] package PowerShell wrappers", flush=True)
    package = ROOT / PACKAGE_NAMES["A"]
    profiles = base / "wrapper-profiles"
    run(
        [
            executable,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(package / "scripts/Install-AgentProfiles.ps1"),
            "-Destination",
            str(profiles),
            "-ExcludeSpark",
        ]
    )
    wrapper_managed = [path for path in profiles.glob("*.toml") if MANAGED in path.read_text(encoding="utf-8", errors="replace")]
    require(len(wrapper_managed) == 15, "Install-AgentProfiles.ps1 installed the wrong profile count")

    codex_home = base / "wrapper-codex"
    env = dict(os.environ, CODEX_HOME=str(codex_home))
    run(
        [
            executable,
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(package / "scripts/Set-Intensity.ps1"),
            "-Mode",
            "heavy",
            "-Scope",
            "user",
        ],
        env=env,
    )
    config = codex_home / "ams-orchestration.toml"
    require(tomllib.loads(config.read_text(encoding="utf-8"))["intensity"] == "heavy", "Set-Intensity.ps1 failed")


def write_process_helpers(base: Path, marker: Path, *, parent_exits: bool, detached_pipes: bool = False) -> Path:
    child = base / f"child-{marker.name}.py"
    child.write_text(
        "import pathlib, sys, time\n"
        "time.sleep(3)\n"
        "pathlib.Path(sys.argv[1]).write_text('orphan', encoding='utf-8')\n",
        encoding="utf-8",
        newline="\n",
    )
    parent = base / f"parent-{marker.name}.py"
    redirection = (
        ", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL"
        if detached_pipes
        else ""
    )
    parent.write_text(
        "import subprocess, sys, time\n"
        f"subprocess.Popen([sys.executable, '-B', '-E', '-s', '-S', sys.argv[1], sys.argv[2]]{redirection})\n"
        + ("" if parent_exits else "time.sleep(30)\n"),
        encoding="utf-8",
        newline="\n",
    )
    return parent


def assert_timeout_cleanup(base: Path, *, parent_exits: bool, fallback: bool = False) -> None:
    marker = base / f"timeout-{'fallback' if fallback else 'job'}-{'exit' if parent_exits else 'live'}"
    parent = write_process_helpers(base, marker, parent_exits=parent_exits)
    old_job = process_utils_module._WindowsJob
    if fallback:
        class DisabledJob:
            active = False
            def __init__(self, process: subprocess.Popen[object]) -> None:
                del process
            def close(self) -> None:
                return
        process_utils_module._WindowsJob = DisabledJob
    try:
        try:
            run_bounded(
                [sys.executable, "-B", "-E", "-s", "-S", str(parent), str(parent.with_name(f"child-{marker.name}.py")), str(marker)],
                timeout=1,
                text=True,
                capture_output=True,
                check=False,
            )
        except subprocess.TimeoutExpired:
            pass
        else:
            raise AssertionError("process-tree command did not time out")
    finally:
        process_utils_module._WindowsJob = old_job
    time.sleep(4)
    require(not marker.exists(), "timed-out Windows process left a descendant running")


def process_contract(base: Path) -> None:
    print("[windows-test] Job Object, fallback, and descendant cleanup", flush=True)
    require(process_is_alive(os.getpid()), "Windows process liveness rejected the current process")
    require(not process_is_alive(2_147_483_647), "Windows process liveness accepted an impossible PID")

    sleeper = subprocess.Popen([sys.executable, "-B", "-E", "-s", "-S", "-c", "import time; time.sleep(30)"])
    job = process_utils_module._WindowsJob(sleeper)
    try:
        require(job.active, "Windows Job Object assignment was unavailable on windows-latest")
    finally:
        job.close()
        with contextlib.suppress(Exception):
            sleeper.wait(timeout=5)

    assert_timeout_cleanup(base, parent_exits=False)
    assert_timeout_cleanup(base, parent_exits=True)
    assert_timeout_cleanup(base, parent_exits=False, fallback=True)

    marker = base / "successful-background"
    parent = write_process_helpers(base, marker, parent_exits=True, detached_pipes=True)
    child = parent.with_name(f"child-{marker.name}.py")
    result = run_bounded(
        [sys.executable, "-B", "-E", "-s", "-S", str(parent), str(child), str(marker)],
        timeout=10,
        text=True,
        capture_output=True,
        check=False,
    )
    require(result.returncode == 0, "successful command returned a failure")
    time.sleep(4)
    require(not marker.exists(), "successful command leaked a background descendant")


def import_module(path: Path, name: str):
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        require(spec is not None and spec.loader is not None, f"cannot load module: {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        with contextlib.suppress(ValueError):
            sys.path.remove(str(path.parent))


def exercise_lock(
    *,
    label: str,
    context_factory,
    lock_path: Path,
) -> None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"pid": os.getpid(), "host": socket.gethostname(), "created": "now"}

    lock_path.write_text(json.dumps(payload), encoding="utf-8", newline="\n")
    try:
        with context_factory():
            raise AssertionError(f"{label} live-owner lock was ignored")
    except SystemExit as exc:
        require("active" in str(exc).lower(), f"{label} live-owner diagnostic is unclear: {exc}")
    lock_path.unlink()

    lock_path.write_text(json.dumps({"pid": 2_147_483_647, "host": socket.gethostname()}), encoding="utf-8")
    old = time.time() - 3 * 60 * 60
    os.utime(lock_path, (old, old))
    with context_factory():
        pass
    require(not lock_path.exists(), f"{label} stale-owner lock was not cleaned")

    lock_path.write_text("{malformed", encoding="utf-8")
    os.utime(lock_path, (old, old))
    with context_factory():
        pass
    require(not lock_path.exists(), f"{label} stale malformed lock was not cleaned")

    lock_path.mkdir()
    try:
        with context_factory():
            raise AssertionError(f"{label} directory lock was ignored")
    except SystemExit as exc:
        require("not a regular file" in str(exc).lower(), f"{label} directory diagnostic is unclear: {exc}")
    lock_path.rmdir()

    target = lock_path.with_name(lock_path.name + ".target")
    target.write_text("target", encoding="utf-8")
    try:
        os.symlink(target, lock_path)
    except OSError:
        pass
    else:
        try:
            with context_factory():
                raise AssertionError(f"{label} symlink lock was ignored")
        except SystemExit as exc:
            require("not a regular file" in str(exc).lower(), f"{label} symlink diagnostic is unclear: {exc}")
        lock_path.unlink()
    target.unlink()

    lock_path.write_text("{}", encoding="utf-8")
    from unittest import mock
    with mock.patch("pathlib.Path.lstat", side_effect=PermissionError("access denied")):
        try:
            with context_factory():
                raise AssertionError(f"{label} permission-denied lock inspection was ignored")
        except SystemExit as exc:
            text = str(exc).lower()
            require("unable to inspect" in text and "access denied" in text, f"{label} permission diagnostic is unclear: {exc}")
    lock_path.unlink()

    with context_factory():
        require(lock_path.exists(), f"{label} lock was not created")
    require(not lock_path.exists(), f"{label} lock was not cleaned after success")

    try:
        with context_factory():
            require(lock_path.exists(), f"{label} lock was not created before failure")
            raise RuntimeError("intentional body failure")
    except RuntimeError:
        pass
    require(not lock_path.exists(), f"{label} lock was not cleaned after failure")


def lock_contract(base: Path) -> None:
    print("[windows-test] package, profile, and intensity lock matrix", flush=True)
    scripts = ROOT / PACKAGE_NAMES["A"] / "scripts"
    installer = import_module(scripts / "install_package.py", "ams_a_install_lock_audit")
    profile = import_module(scripts / "bootstrap_profiles.py", "ams_a_profile_lock_audit")
    intensity = import_module(scripts / "set_intensity.py", "ams_a_intensity_lock_audit")

    market = base / "lock-market"
    exercise_lock(
        label="package install/uninstall",
        context_factory=lambda: installer.install_lock(market),
        lock_path=market / ".ams-install.lock",
    )
    destination = base / "lock-codex" / "agents"
    exercise_lock(
        label="profile installation",
        context_factory=lambda: profile.exclusive_lock(destination),
        lock_path=destination.parent / ".agents.ams-profile-install.lock",
    )
    config = base / "lock-intensity" / "ams-orchestration.toml"
    exercise_lock(
        label="intensity configuration",
        context_factory=lambda: intensity.config_lock(config),
        lock_path=config.parent / ".ams-orchestration-config.lock",
    )


def archive_rejection_contract(executable: str, base: Path) -> None:
    print("[windows-test] archive rejection before home mutation", flush=True)
    cases: list[tuple[str, Path]] = []

    def add_simple(name: str, entry_name: str, data: bytes = b"x") -> None:
        path = base / f"archive-{name}.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(entry_name, data)
        cases.append((name, path))

    add_simple("traversal", "../escape")
    add_simple("absolute", "/absolute")
    add_simple("drive", "C:/drive")
    add_simple("control", "bad\x01name")

    symlink_archive = base / "archive-symlink.zip"
    with zipfile.ZipFile(symlink_archive, "w") as archive:
        info = zipfile.ZipInfo("root/link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(info, "target")
    cases.append(("symlink", symlink_archive))

    duplicate_archive = base / "archive-duplicate.zip"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(duplicate_archive, "w") as archive:
            archive.writestr("root/duplicate", "one")
            archive.writestr("root/duplicate", "two")
    cases.append(("duplicate", duplicate_archive))

    encrypted_archive = base / "archive-encrypted.zip"
    add_simple("encrypted-source", "root/encrypted")
    encrypted_archive.write_bytes((base / "archive-encrypted-source.zip").read_bytes())
    blob = bytearray(encrypted_archive.read_bytes())
    for signature, offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
        position = 0
        while True:
            position = blob.find(signature, position)
            if position < 0:
                break
            flags = struct.unpack_from("<H", blob, position + offset)[0] | 0x1
            struct.pack_into("<H", blob, position + offset, flags)
            position += 4
    encrypted_archive.write_bytes(blob)
    cases.append(("encrypted", encrypted_archive))

    many_archive = base / "archive-many.zip"
    with zipfile.ZipFile(many_archive, "w", compression=zipfile.ZIP_STORED) as archive:
        for index in range(5001):
            archive.writestr(f"root/{index:04d}", b"")
    cases.append(("entry-count", many_archive))

    large_archive = base / "archive-large.zip"
    with zipfile.ZipFile(large_archive, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        with archive.open("root/large", "w") as handle:
            block = b"\0" * (1024 * 1024)
            for _ in range(257):
                handle.write(block)
    cases.append(("expanded-size", large_archive))

    empty_archive = base / "archive-empty.zip"
    with zipfile.ZipFile(empty_archive, "w"):
        pass
    cases.append(("empty", empty_archive))
    malformed = base / "archive-malformed.zip"
    malformed.write_bytes(b"not a zip")
    cases.append(("malformed", malformed))

    missing_package = base / "archive-missing-package.zip"
    add_simple("missing-package-source", "root/readme.txt")
    missing_package.write_bytes((base / "archive-missing-package-source.zip").read_bytes())
    cases.append(("missing-package", missing_package))

    multiple = base / "archive-multiple-package.zip"
    write_archive(multiple, prefixes=("root-one", "root-two"))
    cases.append(("multiple-package", multiple))

    package_a = PACKAGE_NAMES["A"]
    for name, omit, replacements, extras, refresh in (
        (
            "missing-installer",
            {f"{package_a}/scripts/install_package.py"},
            {},
            {},
            None,
        ),
        (
            "missing-manifest",
            {f"{package_a}/MANIFEST.sha256"},
            {},
            {},
            None,
        ),
        (
            "stale-manifest",
            set(),
            {f"{package_a}/MANIFEST.sha256": b"0" * 64 + b"  PACKAGE-OPTION\n"},
            {},
            None,
        ),
        (
            "extra-unlisted",
            set(),
            {},
            {f"{package_a}/extra-unlisted.txt": b"extra"},
            None,
        ),
        (
            "modified-listed",
            set(),
            {f"{package_a}/PACKAGE-OPTION": b"modified\n"},
            {},
            None,
        ),
    ):
        path = base / f"archive-{name}.zip"
        entries = package_entries(replacements=replacements, omit=omit, extras=extras, refresh_package=refresh)
        write_archive(path, entries=entries)
        cases.append((name, path))

    for name, archive in cases:
        home = base / f"reject-home-{name}"
        sentinel = home / "sentinel.bin"
        sentinel.parent.mkdir(parents=True)
        sentinel.write_bytes(b"preserve")
        output = run(ps_command(executable, archive, home, "A"), expect=1, timeout=TIMEOUT)
        require(output.strip(), f"{name} archive failure did not provide a diagnostic")
        require(sentinel.read_bytes() == b"preserve", f"{name} archive rejection changed pre-existing home data")
        require(not (home / ".agents").exists(), f"{name} archive rejection mutated plugin state")
        require(not (home / ".codex").exists(), f"{name} archive rejection mutated Codex state")


def rollback_contract(executable: str, archive: Path, base: Path) -> None:
    print("[windows-test] failed-install rollback", flush=True)
    home, codex_home, project = base / "rollback-home", base / "rollback-codex", base / "rollback-project"
    unrelated = seed_unrelated(home, codex_home, project)
    env = dict(os.environ, CODEX_HOME=str(codex_home))
    run(ps_command(executable, archive, home, "B"), env=env, cwd=project)
    before_market = (home / ".agents/plugins/marketplace.json").read_bytes()
    before_config = (codex_home / "ams-orchestration.toml").read_bytes()
    before_profiles = {path.name: path.read_bytes() for path in (codex_home / "agents").iterdir()}

    package_a = PACKAGE_NAMES["A"]
    failing_bootstrap = (
        b"#!/usr/bin/env python3\n"
        b"import json, sys\n"
        b"if '--dry-run' in sys.argv:\n"
        b"    print(json.dumps({'profiles': []}))\n"
        b"    raise SystemExit(0)\n"
        b"print('intentional profile failure', file=sys.stderr)\n"
        b"raise SystemExit(7)\n"
    )
    entries = package_entries(
        replacements={f"{package_a}/scripts/bootstrap_profiles.py": failing_bootstrap},
        refresh_package=package_a,
    )
    failing_archive = base / "rollback-failing.zip"
    write_archive(failing_archive, entries=entries)
    output = run(ps_command(executable, failing_archive, home, "A"), env=env, cwd=project, expect=1)
    require("failed" in output.lower(), "rollback failure did not provide a clear diagnostic")
    require(active_plugins(home) == [PACKAGE_NAMES["B"]], "failed switch did not restore the previous plugin")
    require((home / ".agents/plugins/marketplace.json").read_bytes() == before_market, "failed switch did not restore marketplace")
    require((codex_home / "ams-orchestration.toml").read_bytes() == before_config, "failed switch did not restore config")
    after_profiles = {path.name: path.read_bytes() for path in (codex_home / "agents").iterdir()}
    require(after_profiles == before_profiles, "failed switch did not restore profiles")
    assert_unrelated(home, codex_home, project, unrelated)
    assert_no_transients(home, codex_home)
    run(uninstall_command(executable, home), env=env, cwd=project)


def offline_uninstall_contract(executable: str, archive: Path, base: Path) -> None:
    print("[windows-test] local, offline, repeated, and orphan-state uninstall", flush=True)
    home, codex_home, project = base / "offline-home", base / "offline-codex", base / "offline-project"
    unrelated = seed_unrelated(home, codex_home, project)
    env = dict(os.environ, CODEX_HOME=str(codex_home))
    run(ps_command(executable, archive, home, "A"), env=env, cwd=project)

    private_bin = base / "offline-bin"
    private_bin.mkdir()
    python_wrapper = private_bin / "python.cmd"
    python_wrapper.write_text(f'@"{sys.executable}" %*\n', encoding="utf-8", newline="\r\n")
    py_wrapper = private_bin / "py.cmd"
    py_wrapper.write_text(f'@"{sys.executable}" %*\n', encoding="utf-8", newline="\r\n")
    offline_env = dict(
        env,
        PATH=str(private_bin),
        HTTP_PROXY="http://127.0.0.1:1",
        HTTPS_PROXY="http://127.0.0.1:1",
        ALL_PROXY="http://127.0.0.1:1",
        AMS_CONNECT_TIMEOUT_SECONDS="1",
        AMS_DOWNLOAD_TIMEOUT_SECONDS="1",
    )
    run(uninstall_command(executable, home), env=offline_env, cwd=project)
    run(uninstall_command(executable, home), env=offline_env, cwd=project)
    assert_uninstalled(home, codex_home, project, unrelated)

    orphan_home, orphan_codex, orphan_project = (
        base / "orphan-home",
        base / "orphan-codex",
        base / "orphan-project",
    )
    unrelated2 = seed_unrelated(orphan_home, orphan_codex, orphan_project)
    orphan_env = dict(os.environ, CODEX_HOME=str(orphan_codex))
    run(ps_command(executable, archive, orphan_home, "C"), env=orphan_env, cwd=orphan_project)
    shutil.rmtree(orphan_home / ".agents/plugins/plugins" / PACKAGE_NAMES["C"])
    backup_root = orphan_home / ".agents/plugins/backups"
    if backup_root.exists():
        shutil.rmtree(backup_root)
    orphan_offline = dict(
        offline_env,
        CODEX_HOME=str(orphan_codex),
    )
    run(uninstall_command(executable, orphan_home), env=orphan_offline, cwd=orphan_project)
    assert_uninstalled(orphan_home, orphan_codex, orphan_project, unrelated2)


def parse_powershell_contract(runtimes: list[tuple[str, str]], base: Path) -> None:
    parser = base / "parse-all.ps1"
    parser.write_text(
        "param([string]$Root)\n"
        "$ErrorActionPreference = 'Stop'\n"
        "$failed = $false\n"
        "Get-ChildItem -LiteralPath $Root -Recurse -Filter *.ps1 | ForEach-Object {\n"
        "  $tokens = $null; $errors = $null\n"
        "  [System.Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$tokens,[ref]$errors) | Out-Null\n"
        "  if ($errors.Count) { $failed = $true; Write-Error ($_.FullName + ': ' + (($errors | ForEach-Object Message) -join '; ')) }\n"
        "}\n"
        "if ($failed) { exit 1 }\n",
        encoding="utf-8",
        newline="\n",
    )
    for label, executable in runtimes:
        print(f"[windows-test] parse all PowerShell files: {label}", flush=True)
        run(
            [
                executable,
                "-NoLogo",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(parser),
                "-Root",
                str(ROOT),
            ],
            timeout=60,
        )


def checkout_and_manifest_contract() -> None:
    print("[windows-test] LF, UTF-8, checkout bytes, and manifests", flush=True)
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    require("* text=auto eol=lf" in attributes, ".gitattributes does not enforce LF")
    bad_cr: list[Path] = []
    bad_bom: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_NAMES:
            continue
        data = path.read_bytes()
        if b"\r" in data:
            bad_cr.append(path)
        if data.startswith(b"\xef\xbb\xbf"):
            bad_bom.append(path)
    require(not bad_cr, f"repository checkout contains CR bytes: {bad_cr}")
    require(not bad_bom, f"repository checkout contains unexpected UTF-8 BOMs: {bad_bom}")
    for package_name in PACKAGE_NAMES.values():
        text = (ROOT / package_name / "PACKAGE-OPTION").read_text(encoding="utf-8")
        require("—" in text or "-" in text, f"PACKAGE-OPTION UTF-8 metadata is unreadable: {package_name}")
    run([sys.executable, "-B", "-E", "-s", "-S", str(ROOT / "scripts/refresh_manifests.py"), "--check"])
    eol = run(["git", "ls-files", "--eol"], cwd=ROOT)
    relevant = [
        line
        for line in eol.splitlines()
        if any(token in line for token in (".ps1", ".py", ".sh", ".md", ".toml", ".json", ".yaml", ".yml", "MANIFEST.sha256", "PACKAGE-OPTION", "VERSION"))
    ]
    require(relevant, "git did not report tracked text files")
    require(all("i/lf" in line and "w/lf" in line for line in relevant), "Git checkout byte normalization is not LF-stable")


def main() -> int:
    require(os.name == "nt", "Windows release tests must run on native Windows")
    runtimes = powershell_runtimes()
    primary = next(executable for label, executable in runtimes if label == "Windows PowerShell 5.1")

    with tempfile.TemporaryDirectory(prefix="ams-windows-release-audit-") as tmp:
        base = Path(tmp)
        archive = base / "repository.zip"
        build_archive(archive)

        parse_powershell_contract(runtimes, base)
        checkout_and_manifest_contract()
        process_contract(base)
        lock_contract(base)

        for label, executable in runtimes:
            lifecycle_matrix(label, executable, archive, base)

        selector_contract(primary, archive, base)
        custom_path_contract(primary, archive, base)
        option_c_skip_profiles_contract(primary, base)
        wrappers_contract(primary, base)
        archive_rejection_contract(primary, base)
        rollback_contract(primary, archive, base)
        offline_uninstall_contract(primary, archive, base)

        require(not generated_artifacts(ROOT), "Windows audit generated Python bytecode in the repository")

    print("WINDOWS INSTALLER TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
