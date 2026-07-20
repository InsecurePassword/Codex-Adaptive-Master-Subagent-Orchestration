#!/usr/bin/env python3
"""Native Windows end-to-end tests for AMS process control and PowerShell installers."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from process_utils import run_bounded  # noqa: E402

TIMEOUT = 120
MANAGED = "# managed-by: adaptive-master-subagent-orchestration"
PACKAGE_NAMES = {
    "A": "adaptive-master-subagent-orchestration-option-a-two-skill",
    "B": "adaptive-master-subagent-orchestration-option-b-unified",
    "C": "adaptive-master-subagent-orchestration-option-c-installer-required",
}
ALL_NAMES = set(PACKAGE_NAMES.values()) | {
    "adaptive-master-subagent-orchestration-option-a-modular",
    "adaptive-master-subagent-orchestration-option-c-lean",
    "adaptive-master-subagent-orchestration",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(command: list[str], *, env: dict[str, str] | None = None, expect: int = 0) -> str:
    try:
        result = run_bounded(
            command,
            timeout=TIMEOUT,
            text=True,
            capture_output=True,
            check=False,
            env=env,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as exc:
        raise AssertionError(f"command timed out after {TIMEOUT}s: {command}") from exc
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != expect:
        raise AssertionError(
            f"command returned {result.returncode}, expected {expect}: {command}\n{output}"
        )
    return output


def build_archive(destination: Path) -> None:
    prefix = "adaptive-master-subagent-orchestration-windows-test"
    included = [ROOT / "install.ps1", ROOT / "install.sh", *(ROOT / name for name in PACKAGE_NAMES.values())]
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in included:
            if source.is_file():
                archive.write(source, f"{prefix}/{source.name}")
                continue
            for path in sorted(source.rglob("*")):
                if path.is_symlink():
                    raise AssertionError(f"test source contains symlink: {path}")
                if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                    continue
                archive.write(path, f"{prefix}/{path.relative_to(ROOT).as_posix()}")


def active_plugins(home: Path) -> list[str]:
    root = home / ".agents" / "plugins" / "plugins"
    if not root.is_dir():
        return []
    return sorted(path.name for path in root.iterdir() if path.name in ALL_NAMES)


def marketplace_plugins(home: Path) -> list[str]:
    path = home / ".agents" / "plugins" / "marketplace.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return sorted(
        item["name"]
        for item in data.get("plugins", [])
        if isinstance(item, dict) and item.get("name") in ALL_NAMES
    )


def require_layout(home: Path, codex_home: Path, option: str) -> None:
    plugin = home / ".agents" / "plugins" / "plugins" / PACKAGE_NAMES[option]
    require((plugin / ".codex-plugin" / "plugin.json").is_file(), f"Option {option} plugin metadata is misplaced")
    require((plugin / "scripts" / "install_package.py").is_file(), f"Option {option} installed package is incomplete")
    require((home / ".agents" / "plugins" / "marketplace.json").is_file(), "marketplace is misplaced")
    require((codex_home / "agents").is_dir(), "managed profile directory is misplaced")
    require((codex_home / "ams-orchestration.toml").is_file(), "user configuration is misplaced")


def write_process_helpers(base: Path, marker: Path, *, parent_exits: bool) -> Path:
    child = base / ("pipe-child.py" if parent_exits else "tree-child.py")
    child.write_text(
        "import pathlib, sys, time\n"
        "time.sleep(3)\n"
        "pathlib.Path(sys.argv[1]).write_text('orphan', encoding='utf-8')\n",
        encoding="utf-8",
        newline="\n",
    )
    parent = base / ("pipe-parent.py" if parent_exits else "tree-parent.py")
    parent.write_text(
        "import subprocess, sys, time\n"
        "subprocess.Popen([sys.executable, '-B', '-E', '-s', '-S', sys.argv[1], sys.argv[2]])\n"
        + ("\n" if parent_exits else "time.sleep(30)\n"),
        encoding="utf-8",
        newline="\n",
    )
    return parent


def assert_process_tree_timeout(base: Path, *, parent_exits: bool) -> None:
    marker = base / ("pipe-orphan" if parent_exits else "tree-orphan")
    parent = write_process_helpers(base, marker, parent_exits=parent_exits)
    child = base / ("pipe-child.py" if parent_exits else "tree-child.py")
    try:
        result = run_bounded(
            [sys.executable, "-B", "-E", "-s", "-S", str(parent), str(child), str(marker)],
            timeout=1,
            text=True,
            capture_output=True,
            check=False,
        )
    except subprocess.TimeoutExpired:
        pass
    else:
        raise AssertionError(
            "process-tree command did not time out; "
            f"returncode={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
    time.sleep(4)
    require(not marker.exists(), "timed-out Windows process left a descendant running")


def powershell_command(executable: str, home: Path, archive: Path, option: str, *extra: str) -> list[str]:
    return [
        executable,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "install.ps1"),
        "-Option",
        option,
        "-ArchivePath",
        str(archive),
        "-HomeDirectory",
        str(home),
        *extra,
    ]


def main() -> int:
    require(os.name == "nt", "Windows release tests must run on Windows")
    executable = shutil.which("powershell.exe") or shutil.which("pwsh") or shutil.which("powershell")
    require(executable is not None, "PowerShell runtime was not found")

    with tempfile.TemporaryDirectory(prefix="ams-windows-release-") as tmp:
        base = Path(tmp)
        archive = base / "repository.zip"
        build_archive(archive)

        print("[windows-test] bounded process-tree cleanup", flush=True)
        assert_process_tree_timeout(base, parent_exits=False)
        print("[windows-test] exited-parent captured-pipe cleanup", flush=True)
        assert_process_tree_timeout(base, parent_exits=True)

        home = base / "home"
        print("[windows-test] Option A install", flush=True)
        run(powershell_command(executable, home, archive, "A", "-ExcludeSpark", "-Intensity", "heavy"))
        require(active_plugins(home) == [PACKAGE_NAMES["A"]], "PowerShell Option A selected the wrong plugin")
        require(marketplace_plugins(home) == [PACKAGE_NAMES["A"]], "PowerShell Option A marketplace entry is wrong")
        require_layout(home, home / ".codex", "A")
        config_path = home / ".codex" / "ams-orchestration.toml"
        config_text = config_path.read_text(encoding="utf-8")
        require(MANAGED in config_text, "PowerShell-created user configuration is not marked as managed")
        require(tomllib.loads(config_text)["intensity"] == "heavy", "PowerShell intensity was not applied")
        require(len(list((home / ".codex" / "agents").glob("*.toml"))) == 15, "PowerShell exclude-Spark was ignored")

        print("[windows-test] switch to Option B", flush=True)
        run(powershell_command(executable, home, archive, "B"))
        require(active_plugins(home) == [PACKAGE_NAMES["B"]], "PowerShell option switch left conflicting plugins")
        require(marketplace_plugins(home) == [PACKAGE_NAMES["B"]], "PowerShell option switch left conflicting marketplace entries")
        require_layout(home, home / ".codex", "B")

        print("[windows-test] Option C with custom CODEX_HOME", flush=True)
        c_home = base / "c-home"
        c_codex = base / "c-codex"
        c_env = dict(os.environ)
        c_env["CODEX_HOME"] = str(c_codex)
        run(powershell_command(executable, c_home, archive, "C", "-ExcludeSpark"), env=c_env)
        require(active_plugins(c_home) == [PACKAGE_NAMES["C"]], "PowerShell Option C selected the wrong plugin")
        require_layout(c_home, c_codex, "C")
        require(not (c_home / ".codex").exists(), "PowerShell custom CODEX_HOME also wrote to the default path")

        print("[windows-test] pre-existing user config preservation", flush=True)
        user_home = base / "user-home"
        user_codex = user_home / ".codex"
        user_codex.mkdir(parents=True)
        user_config = user_codex / "ams-orchestration.toml"
        original = 'schema_version = 1\nintensity = "moderate"\n'
        user_config.write_text(original, encoding="utf-8", newline="\n")
        run(powershell_command(executable, user_home, archive, "A", "-ExcludeSpark"))
        require(user_config.read_text(encoding="utf-8") == original, "PowerShell install changed a pre-existing user config")

        print("[windows-test] uninstall", flush=True)
        for uninstall_home, env in ((home, None), (c_home, c_env), (user_home, None)):
            uninstall = [
                executable,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "install.ps1"),
                "-Option",
                "Uninstall",
                "-HomeDirectory",
                str(uninstall_home),
                "-Force",
            ]
            run(uninstall, env=env)
            run(uninstall, env=env)
            require(active_plugins(uninstall_home) == [], "PowerShell uninstall left an active plugin")
        require(not config_path.exists(), "PowerShell uninstall left a managed config")
        require(not (c_codex / "ams-orchestration.toml").exists(), "PowerShell custom CODEX_HOME uninstall left a managed config")
        require(user_config.read_text(encoding="utf-8") == original, "PowerShell uninstall removed a pre-existing user config")

    print("WINDOWS INSTALLER TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
