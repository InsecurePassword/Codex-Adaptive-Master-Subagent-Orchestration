#!/usr/bin/env python3
"""Offline end-to-end tests for the repository-level AMS installers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from process_utils import run_bounded  # noqa: E402

TIMEOUT = 90
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
    prefix = "adaptive-master-subagent-orchestration-test"
    included = [ROOT / "install.sh", ROOT / "install.ps1", *(ROOT / name for name in PACKAGE_NAMES.values())]
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in included:
            if source.is_file():
                archive.write(source, f"{prefix}/{source.name}")
                continue
            for path in sorted(source.rglob("*")):
                if path.is_symlink():
                    raise AssertionError(f"test source contains symlink: {path}")
                if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                relative = path.relative_to(ROOT).as_posix()
                archive.write(path, f"{prefix}/{relative}")


def marketplace(home: Path) -> dict[str, object]:
    return json.loads((home / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))


def active_plugins(home: Path) -> list[str]:
    plugin_root = home / ".agents" / "plugins" / "plugins"
    if not plugin_root.exists():
        return []
    return sorted(path.name for path in plugin_root.iterdir() if path.name in ALL_NAMES)


def marketplace_plugins(home: Path) -> list[str]:
    return sorted(
        item["name"]
        for item in marketplace(home).get("plugins", [])
        if isinstance(item, dict) and item.get("name") in ALL_NAMES
    )


def test_process_tree_timeout(base: Path) -> None:
    marker = base / "orphan-marker"
    code = (
        "import subprocess,sys,time; "
        f"subprocess.Popen([sys.executable,'-E','-s','-S','-c',\"import time; time.sleep(3); open(r'{marker}', 'w').write('orphan')\"]); "
        "time.sleep(30)"
    )
    try:
        run_bounded(
            [sys.executable, "-E", "-s", "-S", "-c", code],
            timeout=1,
            text=True,
            capture_output=True,
            check=False,
        )
    except subprocess.TimeoutExpired:
        pass
    else:
        raise AssertionError("process-tree timeout test did not time out")
    import time
    time.sleep(4)
    require(not marker.exists(), "timed-out command left an orphaned grandchild process")


def powershell_static_check(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    required = (
        "[CmdletBinding()]",
        "$ErrorActionPreference = \"Stop\"",
        "Set-StrictMode",
        "Get-NormalizedOption",
        "Get-InstalledUninstaller",
        "Expand-SafeArchive",
        "$HomeDirectory",
        "$ArchivePath",
    )
    for token in required:
        require(token in text, f"PowerShell root installer missing {token}")

    lines: list[str] = []
    in_here: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if in_here:
            if stripped == in_here:
                in_here = None
            continue
        if stripped.endswith("@'") or stripped.endswith('@"'):
            in_here = "'@" if stripped.endswith("@'") else '"@'
            continue
        cleaned = ""
        quote: str | None = None
        escape = False
        for char in line:
            if escape:
                escape = False
                continue
            if char == "`":
                escape = True
                continue
            if quote:
                if char == quote:
                    quote = None
                continue
            if char in ("'", '"'):
                quote = char
                continue
            if char == "#":
                break
            cleaned += char
        lines.append(cleaned)
    require(in_here is None, "PowerShell root installer has an unterminated here-string")
    cleaned = "\n".join(lines)
    for opening, closing in (("{", "}"), ("(", ")"), ("[", "]")):
        depth = 0
        for char in cleaned:
            if char == opening:
                depth += 1
            elif char == closing:
                depth -= 1
                require(depth >= 0, f"PowerShell root installer has unmatched {closing}")
        require(depth == 0, f"PowerShell root installer has unmatched {opening}")


def test_powershell_if_available(archive: Path, base: Path) -> None:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    if not executable:
        print("[root-test] PowerShell runtime unavailable; static parser checks completed")
        return
    home = base / "powershell-home"
    command = [
        executable,
        "-NoProfile",
        "-File",
        str(ROOT / "install.ps1"),
        "-Option",
        "A",
        "-ArchivePath",
        str(archive),
        "-HomeDirectory",
        str(home),
        "-ExcludeSpark",
        "-Intensity",
        "heavy",
    ]
    run(command)
    require(active_plugins(home) == [PACKAGE_NAMES["A"]], "PowerShell install selected the wrong option")
    run(
        [
            executable,
            "-NoProfile",
            "-File",
            str(ROOT / "install.ps1"),
            "-Option",
            "Uninstall",
            "-HomeDirectory",
            str(home),
            "-Force",
        ]
    )
    require(active_plugins(home) == [], "PowerShell uninstall left an active plugin")


def main() -> int:
    shell = shutil.which("sh")
    require(shell is not None, "POSIX sh was not found")
    powershell_static_check(ROOT / "install.ps1")

    with tempfile.TemporaryDirectory(prefix="ams-root-installer-tests-") as tmp:
        base = Path(tmp)
        archive = base / "repository.zip"
        build_archive(archive)

        print("[root-test] bounded process-tree cleanup", flush=True)
        test_process_tree_timeout(base)

        print("[root-test] help and invalid arguments", flush=True)
        require("--option" in run([shell, str(ROOT / "install.sh"), "--help"]), "help omitted --option")
        require("Unsupported selection" in run([shell, str(ROOT / "install.sh"), "--option", "Z"], expect=1), "invalid option error unclear")
        require("Interactive input is unavailable" in run([shell, str(ROOT / "install.sh")], expect=1), "noninteractive selector error unclear")

        print("[root-test] Option A CLI install", flush=True)
        home = base / "home"
        market = home / ".agents" / "plugins" / "marketplace.json"
        market.parent.mkdir(parents=True)
        market.write_text(
            json.dumps(
                {
                    "name": "existing",
                    "plugins": [
                        {"name": "unrelated", "source": {"source": "local", "path": "./plugins/unrelated"}}
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        unrelated = home / ".agents" / "plugins" / "plugins" / "unrelated"
        unrelated.mkdir(parents=True)
        (unrelated / "keep.txt").write_text("keep", encoding="utf-8")
        run(
            [
                shell,
                str(ROOT / "install.sh"),
                "--option",
                "A",
                "--archive-path",
                str(archive),
                "--home",
                str(home),
                "--exclude-spark",
                "--intensity",
                "heavy",
            ]
        )
        require(active_plugins(home) == [PACKAGE_NAMES["A"]], "Option A was not the only active option")
        require(marketplace_plugins(home) == [PACKAGE_NAMES["A"]], "marketplace did not contain only Option A")
        require((unrelated / "keep.txt").read_text(encoding="utf-8") == "keep", "unrelated plugin changed")
        config = tomllib.loads((home / ".codex" / "ams-orchestration.toml").read_text(encoding="utf-8"))
        require(config["intensity"] == "heavy", "CLI intensity was not applied")
        require(len(list((home / ".codex" / "agents").glob("*.toml"))) == 15, "exclude-spark was ignored")

        print("[root-test] positional Option B switch", flush=True)
        run([shell, str(ROOT / "install.sh"), "B", "--archive-path", str(archive), "--home", str(home)])
        require(active_plugins(home) == [PACKAGE_NAMES["B"]], "Option switch left multiple active options")
        require(marketplace_plugins(home) == [PACKAGE_NAMES["B"]], "marketplace did not switch to Option B")

        print("[root-test] environment selector", flush=True)
        env_home = base / "env-home"
        env = dict(os.environ)
        env.update(
            AMS_INSTALL_OPTION="C",
            AMS_ARCHIVE_PATH=str(archive),
            AMS_HOME=str(env_home),
            AMS_EXCLUDE_SPARK="1",
        )
        run([shell, str(ROOT / "install.sh")], env=env)
        require(active_plugins(env_home) == [PACKAGE_NAMES["C"]], "environment selector did not install Option C")

        print("[root-test] offline uninstall using installed package", flush=True)
        fake_bin = base / "fake-bin"
        fake_bin.mkdir()
        curl_marker = base / "curl-called"
        fake_curl = fake_bin / "curl"
        fake_curl.write_text(f"#!/bin/sh\ntouch '{curl_marker}'\nexit 99\n", encoding="utf-8")
        fake_curl.chmod(0o755)
        offline_env = dict(os.environ)
        offline_env["PATH"] = str(fake_bin) + os.pathsep + offline_env.get("PATH", "")
        run(
            [shell, str(ROOT / "install.sh"), "--option", "UNINSTALL", "--home", str(home), "--force"],
            env=offline_env,
        )
        require(not curl_marker.exists(), "offline uninstall attempted a download")
        require(active_plugins(home) == [], "offline uninstall left an active option")
        require((unrelated / "keep.txt").exists(), "offline uninstall removed unrelated plugin")

        print("[root-test] archive tamper rejection", flush=True)
        tampered = base / "tampered.zip"
        shutil.copy2(archive, tampered)
        with zipfile.ZipFile(tampered, "a", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                "adaptive-master-subagent-orchestration-test/"
                f"{PACKAGE_NAMES['A']}/README.md",
                "tampered duplicate",
            )
        output = run(
            [shell, str(ROOT / "install.sh"), "--option", "A", "--archive-path", str(tampered), "--home", str(base / "tamper-home")],
            expect=1,
        )
        require("duplicate path" in output.lower(), "duplicate archive path was not rejected")

        print("[root-test] archive traversal rejection", flush=True)
        unsafe = base / "unsafe.zip"
        with zipfile.ZipFile(unsafe, "w") as zf:
            zf.writestr("../escape.txt", "escape")
        output = run(
            [shell, str(ROOT / "install.sh"), "--option", "A", "--archive-path", str(unsafe), "--home", str(base / "unsafe-home")],
            expect=1,
        )
        require("unsafe path" in output.lower(), "archive traversal was not rejected")
        require(not (base / "escape.txt").exists(), "unsafe archive escaped extraction root")

        test_powershell_if_available(archive, base)

    print("ROOT INSTALLER TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
