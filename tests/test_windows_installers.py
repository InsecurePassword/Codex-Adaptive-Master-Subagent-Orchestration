#!/usr/bin/env python3
"""Native Windows end-to-end tests for AMS process control and PowerShell installers."""
from __future__ import annotations

import json
import os
import shutil
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
from process_utils import run_bounded  # noqa: E402

TIMEOUT = 120
ARCHIVE_PREFIX = "adaptive-master-subagent-orchestration-windows-test"
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
    prefix = ARCHIVE_PREFIX
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


def powershell_command(
    executable: str,
    home: Path | None,
    archive: Path | None,
    option: str | None,
    *extra: str,
    option_parameter: str = "-Option",
) -> list[str]:
    command = [
        executable,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "install.ps1"),
    ]
    if option is not None:
        command.extend([option_parameter, option])
    if archive is not None:
        command.extend(["-ArchivePath", str(archive)])
    if home is not None:
        command.extend(["-HomeDirectory", str(home)])
    command.extend(extra)
    return command


def powershell_runtimes() -> list[str]:
    candidates = [shutil.which("powershell.exe"), shutil.which("pwsh.exe"), shutil.which("pwsh"), shutil.which("powershell")]
    unique: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate:
            continue
        key = os.path.normcase(os.path.realpath(candidate))
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def patch_zip_flags(path: Path, flag_mask: int) -> None:
    data = bytearray(path.read_bytes())
    offset = 0
    while True:
        offset = data.find(b"PK\x03\x04", offset)
        if offset < 0:
            break
        flags = struct.unpack_from("<H", data, offset + 6)[0]
        struct.pack_into("<H", data, offset + 6, flags | flag_mask)
        offset += 4
    offset = 0
    while True:
        offset = data.find(b"PK\x01\x02", offset)
        if offset < 0:
            break
        flags = struct.unpack_from("<H", data, offset + 8)[0]
        struct.pack_into("<H", data, offset + 8, flags | flag_mask)
        offset += 4
    path.write_bytes(data)


def patch_zip_uncompressed_size(path: Path, size: int) -> None:
    data = bytearray(path.read_bytes())
    local = data.find(b"PK\x03\x04")
    central = data.find(b"PK\x01\x02")
    require(local >= 0 and central >= 0, "test ZIP headers were not found")
    struct.pack_into("<I", data, local + 22, size)
    struct.pack_into("<I", data, central + 24, size)
    path.write_bytes(data)


def rewrite_archive(
    source: Path,
    destination: Path,
    *,
    remove: set[str] | None = None,
    replacements: dict[str, bytes | str] | None = None,
    additions: dict[str, bytes | str] | None = None,
) -> None:
    remove = remove or set()
    replacements = replacements or {}
    additions = additions or {}
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as changed:
        for info in original.infolist():
            if info.filename in remove:
                continue
            changed.writestr(info, replacements.get(info.filename, original.read(info)))
        for name, data in additions.items():
            changed.writestr(name, data)


def assert_archive_rejected(executable: str, archive: Path, home: Path, expected: str) -> None:
    output = run(powershell_command(executable, home, archive, "A"), expect=1)
    require(expected.lower() in output.lower(), f"PowerShell archive rejection did not report {expected!r}: {output}")
    require(not home.exists(), f"PowerShell archive rejection mutated installation home: {home}")


def test_archive_rejections(executable: str, valid_archive: Path, base: Path) -> None:
    root = base / "archive-rejections"
    root.mkdir(parents=True)
    cases: list[tuple[str, Path, str]] = []

    empty = root / "empty.zip"
    with zipfile.ZipFile(empty, "w"):
        pass
    cases.append(("empty", empty, "archive is empty"))

    malformed = root / "malformed.zip"
    malformed.write_bytes(b"not a zip")
    cases.append(("malformed", malformed, "could not be extracted"))

    for label, name, expected in (
        ("traversal", "../escape", "unsafe path"),
        ("absolute", "/absolute", "unsafe path"),
        ("drive", "C:/drive", "drive path"),
        ("control", f"root/bad{chr(1)}name", "control character"),
    ):
        archive = root / f"{label}.zip"
        with zipfile.ZipFile(archive, "w") as changed:
            changed.writestr(name, "x")
        cases.append((label, archive, expected))

    linked = root / "symlink.zip"
    link_info = zipfile.ZipInfo("root/link")
    link_info.create_system = 3
    link_info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(linked, "w") as changed:
        changed.writestr(link_info, "target")
    cases.append(("symlink", linked, "symbolic link"))

    encrypted = root / "encrypted.zip"
    with zipfile.ZipFile(encrypted, "w") as changed:
        changed.writestr("root/file", "x")
    patch_zip_flags(encrypted, 0x1)
    cases.append(("encrypted", encrypted, "encrypted entry"))

    excessive_entries = root / "too-many.zip"
    with zipfile.ZipFile(excessive_entries, "w", compression=zipfile.ZIP_STORED) as changed:
        for index in range(5001):
            changed.writestr(f"root/{index}", b"")
    cases.append(("too-many", excessive_entries, "too many entries"))

    oversized = root / "oversized.zip"
    with zipfile.ZipFile(oversized, "w") as changed:
        changed.writestr("root/file", "x")
    patch_zip_uncompressed_size(oversized, 256 * 1024 * 1024 + 1)
    cases.append(("oversized", oversized, "extraction size limit"))

    missing_package = root / "missing-package.zip"
    with zipfile.ZipFile(missing_package, "w") as changed:
        changed.writestr("root/README.md", "x")
    cases.append(("missing-package", missing_package, "found 0"))

    multiple_package = root / "multiple-package.zip"
    with zipfile.ZipFile(multiple_package, "w") as changed:
        for prefix in ("one", "two"):
            changed.writestr(f"{prefix}/{PACKAGE_NAMES['A']}/scripts/install_package.py", "pass\n")
    cases.append(("multiple-package", multiple_package, "found 2"))

    package_prefix = f"{ARCHIVE_PREFIX}/{PACKAGE_NAMES['A']}"
    manifest_path = f"{package_prefix}/MANIFEST.sha256"
    readme_path = f"{package_prefix}/README.md"

    duplicate_archive = root / "duplicate-archive.zip"
    shutil.copy2(valid_archive, duplicate_archive)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(duplicate_archive, "a", compression=zipfile.ZIP_DEFLATED) as changed:
            changed.writestr(readme_path, "duplicate")
    cases.append(("duplicate-archive", duplicate_archive, "duplicate path"))

    missing_manifest = root / "missing-manifest.zip"
    rewrite_archive(valid_archive, missing_manifest, remove={manifest_path})
    cases.append(("missing-manifest", missing_manifest, "manifest"))

    malformed_manifest = root / "malformed-manifest.zip"
    rewrite_archive(valid_archive, malformed_manifest, replacements={manifest_path: "not-a-manifest\n"})
    cases.append(("malformed-manifest", malformed_manifest, "malformed package manifest"))

    with zipfile.ZipFile(valid_archive) as original:
        manifest_text = original.read(manifest_path).decode("utf-8")
    first_manifest_line = next(line for line in manifest_text.splitlines() if line.strip())
    duplicate_manifest = root / "duplicate-manifest.zip"
    rewrite_archive(valid_archive, duplicate_manifest, replacements={manifest_path: manifest_text + first_manifest_line + "\n"})
    cases.append(("duplicate-manifest", duplicate_manifest, "duplicate package manifest"))

    unlisted = root / "unlisted.zip"
    rewrite_archive(valid_archive, unlisted, additions={f"{package_prefix}/unlisted.txt": "x"})
    cases.append(("unlisted", unlisted, "unlisted"))

    missing_listed = root / "missing-listed.zip"
    rewrite_archive(valid_archive, missing_listed, remove={readme_path})
    cases.append(("missing-listed", missing_listed, "missing"))

    changed = root / "changed.zip"
    rewrite_archive(valid_archive, changed, replacements={readme_path: "changed\n"})
    cases.append(("changed", changed, "changed=["))

    bytecode = root / "bytecode.zip"
    rewrite_archive(valid_archive, bytecode, additions={f"{package_prefix}/scripts/__pycache__/audit.pyc": b"generated"})
    cases.append(("bytecode", bytecode, "generated python artifact"))

    for label, archive, expected in cases:
        assert_archive_rejected(executable, archive, root / f"home-{label}", expected)


def test_symlinked_uninstaller_rejection(executable: str, base: Path) -> None:
    for case in ("active-package", "backup-package", "backup-root"):
        home = base / f"symlink-uninstaller-{case}-home"
        plugin_root = home / ".agents" / "plugins" / "plugins"
        backup_root = home / ".agents" / "plugins" / "backups"
        plugin_root.mkdir(parents=True)
        outside = base / f"external-uninstaller-{case}"
        external_package = outside / f"{PACKAGE_NAMES['A']}.backup-20260720-000000" if case == "backup-root" else outside
        (external_package / "scripts").mkdir(parents=True)
        marker = base / f"external-uninstaller-{case}-executed"
        (external_package / "scripts" / "install_package.py").write_text(
            "from pathlib import Path\n" + f"Path({str(marker)!r}).write_text('executed', encoding='utf-8')\n",
            encoding="utf-8",
            newline="\n",
        )
        try:
            if case == "active-package":
                (plugin_root / PACKAGE_NAMES["A"]).symlink_to(outside, target_is_directory=True)
                unsafe_path = plugin_root / PACKAGE_NAMES["A"]
            elif case == "backup-package":
                backup_root.mkdir(parents=True)
                unsafe_path = backup_root / f"{PACKAGE_NAMES['A']}.backup-20260720-000000"
                unsafe_path.symlink_to(outside, target_is_directory=True)
            else:
                unsafe_path = backup_root
                unsafe_path.symlink_to(outside, target_is_directory=True)
        except OSError:
            print("[windows-test] symlink privilege unavailable; symlinked uninstaller runtime checks skipped", flush=True)
            return
        output = run(powershell_command(executable, home, None, "Uninstall", "-Force"), expect=1)
        require("unsafe ams uninstaller path" in output.lower(), f"PowerShell {case} uninstaller rejection was unclear")
        require(not marker.exists(), f"PowerShell root uninstall executed an external uninstaller through {case}")
        require(unsafe_path.is_symlink(), f"PowerShell safe discovery mutated the {case} symlink")


def run_runtime_suite(executable: str, archive: Path, base: Path) -> None:
    runtime_name = Path(executable).stem.lower()
    suite = base / runtime_name
    suite.mkdir(parents=True, exist_ok=True)

    home = suite / "lifecycle-home"
    precedence_env = dict(os.environ)
    precedence_env["AMS_INTENSITY"] = "minimal"
    precedence_env["AMS_SPARK_EFFORTS"] = "high"
    print(f"[windows-test:{runtime_name}] Option A alias and CLI precedence", flush=True)
    run(
        powershell_command(
            executable,
            home,
            archive,
            "A",
            "-Intensity",
            "heavy",
            "-SparkEfforts",
            "low",
            option_parameter="-InstallOption",
        ),
        env=precedence_env,
    )
    require(active_plugins(home) == [PACKAGE_NAMES["A"]], "PowerShell alias selected the wrong Option A plugin")
    require_layout(home, home / ".codex", "A")
    config_path = home / ".codex" / "ams-orchestration.toml"
    config_text = config_path.read_text(encoding="utf-8")
    require(config_text.splitlines()[0] == MANAGED, "PowerShell-created user configuration marker is not the first line")
    require(tomllib.loads(config_text)["intensity"] == "heavy", "explicit PowerShell intensity did not override the environment")
    require(len(list((home / ".codex" / "agents").glob("*.toml"))) == 16, "explicit PowerShell Spark efforts did not override the environment")

    print(f"[windows-test:{runtime_name}] A reinstall and A to B switch", flush=True)
    run(powershell_command(executable, home, archive, "A"))
    run(powershell_command(executable, home, archive, "B"))
    require(active_plugins(home) == [PACKAGE_NAMES["B"]], "PowerShell A-to-B switch left conflicting plugins")
    require(marketplace_plugins(home) == [PACKAGE_NAMES["B"]], "PowerShell A-to-B switch left conflicting marketplace entries")

    print(f"[windows-test:{runtime_name}] Option C with spaces, Unicode, nested, and long paths", flush=True)
    c_home = suite / "home with spaces" / "用户-Δ" / ("nested-" + "h" * 64)
    c_codex = suite / "codex with spaces" / "配置-λ" / ("nested-" + "c" * 64)
    c_env = dict(os.environ)
    c_env["CODEX_HOME"] = str(c_codex)
    run(powershell_command(executable, c_home, archive, "C", "-ExcludeSpark"), env=c_env)
    require(active_plugins(c_home) == [PACKAGE_NAMES["C"]], "PowerShell Option C selected the wrong plugin")
    require_layout(c_home, c_codex, "C")
    require(not (c_home / ".codex").exists(), "PowerShell custom CODEX_HOME also wrote to the default path")

    print(f"[windows-test:{runtime_name}] numeric selections", flush=True)
    numeric_home = suite / "numeric-home"
    for numeric, option in (("1", "A"), ("2", "B"), ("3", "C")):
        run(powershell_command(executable, numeric_home, archive, numeric, "-ExcludeSpark"))
        require(active_plugins(numeric_home) == [PACKAGE_NAMES[option]], f"PowerShell numeric selection {numeric} selected the wrong plugin")
    run(powershell_command(executable, numeric_home, None, "4", "-Force"))
    require(active_plugins(numeric_home) == [], "PowerShell numeric uninstall did not remove the package")

    print(f"[windows-test:{runtime_name}] environment selections", flush=True)
    env_home = suite / "environment-home"
    for selection, option in (("A", "A"), ("B", "B"), ("C", "C")):
        selection_env = dict(os.environ)
        selection_env.update(AMS_INSTALL_OPTION=selection, AMS_ARCHIVE_PATH=str(archive), AMS_HOME=str(env_home), AMS_EXCLUDE_SPARK="1")
        run(powershell_command(executable, None, None, None), env=selection_env)
        require(active_plugins(env_home) == [PACKAGE_NAMES[option]], f"PowerShell environment selection {selection} selected the wrong plugin")
    uninstall_env = dict(os.environ)
    uninstall_env.update(AMS_INSTALL_OPTION="4", AMS_HOME=str(env_home), AMS_UNINSTALL_FORCE="1")
    run(powershell_command(executable, None, None, None), env=uninstall_env)
    require(active_plugins(env_home) == [], "PowerShell environment uninstall did not remove the package")

    print(f"[windows-test:{runtime_name}] ownership-safe user configuration", flush=True)
    user_home = suite / "user-home"
    user_codex = user_home / ".codex"
    user_codex.mkdir(parents=True)
    user_config = user_codex / "ams-orchestration.toml"
    original = (
        'schema_version = 1\n'
        'intensity = "moderate"\n'
        'note = "# managed-by: adaptive-master-subagent-orchestration"\n'
    )
    user_config.write_text(original, encoding="utf-8", newline="\n")
    run(powershell_command(executable, user_home, archive, "A", "-ExcludeSpark"))
    require(user_config.read_text(encoding="utf-8") == original, "PowerShell install changed a pre-existing marker-value user config")

    print(f"[windows-test:{runtime_name}] local idempotent uninstall", flush=True)
    for uninstall_home, env in ((home, None), (c_home, c_env), (user_home, None)):
        uninstall = powershell_command(executable, uninstall_home, None, "Uninstall", "-Force")
        run(uninstall, env=env)
        run(uninstall, env=env)
        require(active_plugins(uninstall_home) == [], "PowerShell uninstall left an active plugin")
    require(not config_path.exists(), "PowerShell uninstall left a managed config")
    require(not (c_codex / "ams-orchestration.toml").exists(), "PowerShell custom CODEX_HOME uninstall left a managed config")
    require(user_config.read_text(encoding="utf-8") == original, "PowerShell uninstall removed a pre-existing marker-value user config")

    print(f"[windows-test:{runtime_name}] archive rejection", flush=True)
    test_archive_rejections(executable, archive, suite)
    print(f"[windows-test:{runtime_name}] symlinked uninstaller rejection", flush=True)
    test_symlinked_uninstaller_rejection(executable, suite)


def main() -> int:
    require(os.name == "nt", "Windows release tests must run on Windows")
    runtimes = powershell_runtimes()
    require(runtimes, "PowerShell runtime was not found")

    with tempfile.TemporaryDirectory(prefix="ams-windows-release-") as tmp:
        base = Path(tmp)
        archive = base / "repository.zip"
        build_archive(archive)

        print("[windows-test] bounded process-tree cleanup", flush=True)
        assert_process_tree_timeout(base, parent_exits=False)
        print("[windows-test] exited-parent captured-pipe cleanup", flush=True)
        assert_process_tree_timeout(base, parent_exits=True)

        for executable in runtimes:
            print(f"[windows-test] runtime: {executable}", flush=True)
            run_runtime_suite(executable, archive, base)

    print("WINDOWS INSTALLER TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
