#!/usr/bin/env python3
"""Offline end-to-end tests for the repository-level AMS installers."""

from __future__ import annotations

import json
import os
import select
import shlex
import shutil
import signal
import stat
import struct
import subprocess
import sys
import time

sys.dont_write_bytecode = True
import tempfile
import tomllib
import warnings
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from process_utils import run_bounded  # noqa: E402

TIMEOUT = 90
ARCHIVE_PREFIX = "adaptive-master-subagent-orchestration-test"
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


def run_with_tty(command: list[str], input_text: str, *, env: dict[str, str] | None = None, expect: int = 0) -> str:
    """Run a command with a controlling terminal while preserving script stdin semantics."""
    import pty

    child_env = dict(os.environ)
    if env:
        child_env.update(env)
    pid, master = pty.fork()
    if pid == 0:
        os.execvpe(command[0], command, child_env)
    output = bytearray()
    deadline = time.monotonic() + TIMEOUT
    try:
        os.write(master, input_text.encode("utf-8"))
        status: int | None = None
        while status is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                try:
                    os.killpg(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                os.waitpid(pid, 0)
                raise AssertionError(f"interactive command timed out after {TIMEOUT}s: {command}")
            readable, _, _ = select.select([master], [], [], min(0.1, remaining))
            if readable:
                try:
                    block = os.read(master, 65536)
                except OSError:
                    block = b""
                output.extend(block)
            waited, child_status = os.waitpid(pid, os.WNOHANG)
            if waited == pid:
                status = child_status
        while True:
            readable, _, _ = select.select([master], [], [], 0)
            if not readable:
                break
            try:
                block = os.read(master, 65536)
            except OSError:
                break
            if not block:
                break
            output.extend(block)
    finally:
        os.close(master)
    code = os.waitstatus_to_exitcode(status)
    decoded = output.decode("utf-8", errors="replace")
    if code != expect:
        raise AssertionError(f"interactive command returned {code}, expected {expect}: {command}\n{decoded}")
    return decoded


def rewrite_archive(
    source: Path,
    destination: Path,
    *,
    remove: set[str] | None = None,
    replacements: dict[str, bytes | str] | None = None,
    additions: dict[str, bytes | str | zipfile.ZipInfo] | None = None,
) -> None:
    remove = remove or set()
    replacements = replacements or {}
    additions = additions or {}
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as changed:
        for info in original.infolist():
            if info.filename in remove:
                continue
            data: bytes | str = replacements.get(info.filename, original.read(info))
            changed.writestr(info, data)
        for name, data in additions.items():
            if isinstance(data, zipfile.ZipInfo):
                changed.writestr(data, "target")
            else:
                changed.writestr(name, data)


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


def assert_archive_rejected(shell: str, archive: Path, home: Path, expected: str) -> str:
    output = run(
        [shell, str(ROOT / "install.sh"), "--option", "A", "--archive-path", str(archive), "--home", str(home)],
        expect=1,
    )
    require(expected.lower() in output.lower(), f"archive rejection did not report {expected!r}: {output}")
    require(not home.exists(), f"archive rejection mutated installation home: {home}")
    return output


def test_selector_matrix(shell: str, archive: Path, base: Path) -> None:
    cases: list[tuple[str, list[str], dict[str, str], str]] = [
        ("named-b", ["--option", "B"], {}, "B"),
        ("named-c", ["--option", "C"], {}, "C"),
        ("positional-a", ["A"], {}, "A"),
        ("positional-c", ["C"], {}, "C"),
        ("numeric-1", ["--option", "1"], {}, "A"),
        ("numeric-2", ["--option", "2"], {}, "B"),
        ("numeric-3", ["--option", "3"], {}, "C"),
        ("environment-a", [], {"AMS_INSTALL_OPTION": "A"}, "A"),
        ("environment-b", [], {"AMS_INSTALL_OPTION": "B"}, "B"),
    ]
    homes: dict[str, Path] = {}
    for label, selector, extra_env, option in cases:
        home = base / "selection-matrix" / label
        homes[label] = home
        env = dict(os.environ)
        env.update(extra_env)
        command = [shell, str(ROOT / "install.sh"), *selector, "--archive-path", str(archive), "--home", str(home), "--exclude-spark"]
        run(command, env=env)
        require(active_plugins(home) == [PACKAGE_NAMES[option]], f"{label} selected the wrong package")
        require_install_layout(home, home / ".codex", option)
    numeric_home = homes["numeric-1"]
    run([shell, str(ROOT / "install.sh"), "--option", "4", "--home", str(numeric_home), "--force"])
    require(active_plugins(numeric_home) == [], "numeric uninstall selection did not remove the package")
    for label in ("named-b", "named-c"):
        uninstall_home = homes[label]
        run([shell, str(ROOT / "install.sh"), "--option", "UNINSTALL", "--home", str(uninstall_home), "--force"])
        require(active_plugins(uninstall_home) == [], f"root uninstall failed for {label}")


def test_interactive_selection(shell: str, archive: Path, base: Path) -> None:
    interactive_home = base / "interactive-default-home"
    output = run_with_tty(
        [shell, str(ROOT / "install.sh"), "--archive-path", str(archive), "--home", str(interactive_home), "--exclude-spark"],
        "\n",
    )
    require("Selection [1]" in output, "interactive menu was not displayed")
    require(active_plugins(interactive_home) == [PACKAGE_NAMES["A"]], "Enter did not select Option A")

    piped_home = base / "piped-interactive-home"
    pipeline = (
        f"cat {shlex.quote(str(ROOT / 'install.sh'))} | {shlex.quote(shell)} -s -- "
        f"--archive-path {shlex.quote(str(archive))} --home {shlex.quote(str(piped_home))} --exclude-spark"
    )
    output = run_with_tty([shell, "-c", pipeline], "\n")
    require("Selection [1]" in output, "piped installer did not read its menu through the terminal")
    require(active_plugins(piped_home) == [PACKAGE_NAMES["A"]], "piped interactive Enter did not select Option A")


def test_archive_rejections(shell: str, valid_archive: Path, base: Path) -> None:
    rejection_root = base / "archive-rejections"
    rejection_root.mkdir()

    cases: list[tuple[str, Path, str]] = []
    empty = rejection_root / "empty.zip"
    with zipfile.ZipFile(empty, "w"):
        pass
    cases.append(("empty", empty, "archive is empty"))

    malformed = rejection_root / "malformed.zip"
    malformed.write_bytes(b"not a zip")
    cases.append(("malformed", malformed, "could not be extracted"))

    simple_specs = [
        ("traversal", "../escape.txt", "unsafe path"),
        ("absolute", "/absolute.txt", "unsafe path"),
        ("drive", "C:/drive.txt", "drive path"),
        ("control", f"root/bad{chr(1)}name", "control character"),
    ]
    for label, name, expected in simple_specs:
        path = rejection_root / f"{label}.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(name, "x")
        cases.append((label, path, expected))

    linked = rejection_root / "symlink.zip"
    link_info = zipfile.ZipInfo("root/link")
    link_info.create_system = 3
    link_info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(linked, "w") as archive:
        archive.writestr(link_info, "target")
    cases.append(("symlink", linked, "symbolic link"))

    encrypted = rejection_root / "encrypted.zip"
    with zipfile.ZipFile(encrypted, "w") as archive:
        archive.writestr("root/file", "x")
    patch_zip_flags(encrypted, 0x1)
    cases.append(("encrypted", encrypted, "encrypted entry"))

    excessive_entries = rejection_root / "too-many.zip"
    with zipfile.ZipFile(excessive_entries, "w", compression=zipfile.ZIP_STORED) as archive:
        for index in range(5001):
            archive.writestr(f"root/{index}", b"")
    cases.append(("too-many", excessive_entries, "too many entries"))

    oversized = rejection_root / "oversized.zip"
    with zipfile.ZipFile(oversized, "w") as archive:
        archive.writestr("root/file", "x")
    patch_zip_uncompressed_size(oversized, 256 * 1024 * 1024 + 1)
    cases.append(("oversized", oversized, "extraction size limit"))

    missing_package = rejection_root / "missing-package.zip"
    with zipfile.ZipFile(missing_package, "w") as archive:
        archive.writestr("root/README.md", "x")
    cases.append(("missing-package", missing_package, "found 0"))

    multiple_package = rejection_root / "multiple-package.zip"
    with zipfile.ZipFile(multiple_package, "w") as archive:
        for prefix in ("one", "two"):
            archive.writestr(f"{prefix}/{PACKAGE_NAMES['A']}/scripts/install_package.py", "pass\n")
    cases.append(("multiple-package", multiple_package, "found 2"))

    package_prefix = f"{ARCHIVE_PREFIX}/{PACKAGE_NAMES['A']}"
    manifest_path = f"{package_prefix}/MANIFEST.sha256"
    readme_path = f"{package_prefix}/README.md"

    duplicate_archive = rejection_root / "duplicate-archive.zip"
    shutil.copy2(valid_archive, duplicate_archive)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(duplicate_archive, "a", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(readme_path, "duplicate")
    cases.append(("duplicate-archive", duplicate_archive, "duplicate path"))

    missing_manifest = rejection_root / "missing-manifest.zip"
    rewrite_archive(valid_archive, missing_manifest, remove={manifest_path})
    cases.append(("missing-manifest", missing_manifest, "manifest"))

    malformed_manifest = rejection_root / "malformed-manifest.zip"
    rewrite_archive(valid_archive, malformed_manifest, replacements={manifest_path: "not-a-manifest\n"})
    cases.append(("malformed-manifest", malformed_manifest, "malformed package manifest"))

    with zipfile.ZipFile(valid_archive) as archive:
        original_manifest = archive.read(manifest_path).decode("utf-8")
    first_manifest_line = next(line for line in original_manifest.splitlines() if line.strip())
    duplicate_manifest = rejection_root / "duplicate-manifest.zip"
    rewrite_archive(valid_archive, duplicate_manifest, replacements={manifest_path: original_manifest + first_manifest_line + "\n"})
    cases.append(("duplicate-manifest", duplicate_manifest, "duplicate package manifest"))

    unlisted = rejection_root / "unlisted.zip"
    rewrite_archive(valid_archive, unlisted, additions={f"{package_prefix}/unlisted.txt": "x"})
    cases.append(("unlisted", unlisted, "unlisted"))

    missing_listed = rejection_root / "missing-listed.zip"
    rewrite_archive(valid_archive, missing_listed, remove={readme_path})
    cases.append(("missing-listed", missing_listed, "missing"))

    changed = rejection_root / "changed.zip"
    rewrite_archive(valid_archive, changed, replacements={readme_path: "changed\n"})
    cases.append(("changed", changed, "changed=["))

    bytecode = rejection_root / "bytecode.zip"
    rewrite_archive(valid_archive, bytecode, additions={f"{package_prefix}/scripts/__pycache__/audit.pyc": b"generated"})
    cases.append(("bytecode", bytecode, "generated python artifact"))

    for label, archive, expected in cases:
        assert_archive_rejected(shell, archive, rejection_root / f"home-{label}", expected)


def test_symlinked_uninstaller_rejection(shell: str, base: Path) -> None:
    if not hasattr(os, "symlink"):
        return
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
            return
        output = run(
            [shell, str(ROOT / "install.sh"), "--option", "UNINSTALL", "--home", str(home), "--force"],
            expect=1,
        )
        require("unsafe ams uninstaller path" in output.lower(), f"{case} uninstaller rejection was unclear")
        require(not marker.exists(), f"root uninstall executed an external uninstaller through {case}")
        require(unsafe_path.is_symlink(), f"failed safe discovery mutated the {case} symlink")


def build_archive(destination: Path) -> None:
    prefix = ARCHIVE_PREFIX
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


def require_install_layout(home: Path, codex_home: Path, option: str) -> None:
    plugin = home / ".agents" / "plugins" / "plugins" / PACKAGE_NAMES[option]
    require((plugin / ".codex-plugin" / "plugin.json").is_file(), f"Option {option} plugin metadata is misplaced")
    require((plugin / "scripts" / "install_package.py").is_file(), f"Option {option} installer is missing from installed plugin")
    require((home / ".agents" / "plugins" / "marketplace.json").is_file(), "marketplace file is misplaced")
    require((codex_home / "agents").is_dir(), "managed profiles directory is misplaced")
    require((codex_home / "ams-orchestration.toml").is_file(), "user configuration is misplaced")


def test_process_tree_timeout(base: Path) -> None:
    marker = base / "orphan-marker"
    code = (
        "import subprocess,sys,time; "
        f"subprocess.Popen([sys.executable,'-E','-s','-S','-c',\"import time; time.sleep(3); open(r'{marker}', 'w').write('orphan')\"]); "
        "time.sleep(30)"
    )
    try:
        run_bounded(
            [sys.executable, "-B", "-E", "-s", "-S", "-c", code],
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


def test_exited_parent_pipe_cleanup(base: Path) -> None:
    marker = base / "exited-parent-orphan-marker"
    child = f"import time; time.sleep(3); open(r'{marker}', 'w').write('orphan')"
    parent = (
        "import subprocess,sys; "
        "subprocess.Popen([sys.executable,'-E','-s','-S','-c'," + repr(child) + "])"
    )
    try:
        run_bounded(
            [sys.executable, "-B", "-E", "-s", "-S", "-c", parent],
            timeout=1,
            text=True,
            capture_output=True,
            check=False,
        )
    except subprocess.TimeoutExpired:
        pass
    else:
        raise AssertionError("exited-parent pipe test did not time out")
    import time
    time.sleep(4)
    require(not marker.exists(), "exited parent left a descendant holding captured pipes")


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
    require_install_layout(home, home / ".codex", "A")
    run([executable, "-NoProfile", "-File", str(ROOT / "install.ps1"), "-Option", "B", "-ArchivePath", str(archive), "-HomeDirectory", str(home)])
    require(active_plugins(home) == [PACKAGE_NAMES["B"]], "PowerShell option switch left multiple active plugins")
    require_install_layout(home, home / ".codex", "B")
    c_home = base / "powershell-c-home"
    run([executable, "-NoProfile", "-File", str(ROOT / "install.ps1"), "-Option", "C", "-ArchivePath", str(archive), "-HomeDirectory", str(c_home), "-ExcludeSpark"])
    require(active_plugins(c_home) == [PACKAGE_NAMES["C"]], "PowerShell Option C installed the wrong plugin")
    require_install_layout(c_home, c_home / ".codex", "C")
    for uninstall_home in (home, c_home):
        run([executable, "-NoProfile", "-File", str(ROOT / "install.ps1"), "-Option", "Uninstall", "-HomeDirectory", str(uninstall_home), "-Force"])
        require(active_plugins(uninstall_home) == [], "PowerShell uninstall left an active plugin")


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
        print("[root-test] exited-parent captured-pipe cleanup", flush=True)
        test_exited_parent_pipe_cleanup(base)

        print("[root-test] help and invalid arguments", flush=True)
        require("--option" in run([shell, str(ROOT / "install.sh"), "--help"]), "help omitted --option")
        require("Unsupported selection" in run([shell, str(ROOT / "install.sh"), "--option", "Z"], expect=1), "invalid option error unclear")
        require("Interactive input is unavailable" in run([shell, str(ROOT / "install.sh")], expect=1), "noninteractive selector error unclear")
        empty_spark_env = dict(os.environ)
        empty_spark_env.update(AMS_INSTALL_OPTION="A", AMS_ARCHIVE_PATH=str(archive), AMS_HOME=str(base / "empty-spark-home"), AMS_EXCLUDE_SPARK="1", AMS_SPARK_EFFORTS="")
        run([shell, str(ROOT / "install.sh")], env=empty_spark_env)
        require(len(list((base / "empty-spark-home/.codex/agents").glob("*.toml"))) == 15, "empty Spark list with exclusion failed")

        print("[root-test] complete selector matrix", flush=True)
        test_selector_matrix(shell, archive, base)
        print("[root-test] interactive and piped menu", flush=True)
        test_interactive_selection(shell, archive, base)

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
        require_install_layout(home, home / ".codex", "A")

        print("[root-test] positional Option B switch", flush=True)
        run([shell, str(ROOT / "install.sh"), "B", "--archive-path", str(archive), "--home", str(home)])
        require(active_plugins(home) == [PACKAGE_NAMES["B"]], "Option switch left multiple active options")
        require(marketplace_plugins(home) == [PACKAGE_NAMES["B"]], "marketplace did not switch to Option B")

        print("[root-test] B to C, C to A, and A reinstall", flush=True)
        run([shell, str(ROOT / "install.sh"), "--option", "C", "--archive-path", str(archive), "--home", str(home)])
        require(active_plugins(home) == [PACKAGE_NAMES["C"]], "B-to-C switch left conflicting plugins")
        require(marketplace_plugins(home) == [PACKAGE_NAMES["C"]], "B-to-C switch left conflicting marketplace entries")
        run([shell, str(ROOT / "install.sh"), "--option", "A", "--archive-path", str(archive), "--home", str(home)])
        require(active_plugins(home) == [PACKAGE_NAMES["A"]], "C-to-A switch left conflicting plugins")
        require(marketplace_plugins(home) == [PACKAGE_NAMES["A"]], "C-to-A switch left conflicting marketplace entries")
        run([shell, str(ROOT / "install.sh"), "--option", "A", "--archive-path", str(archive), "--home", str(home)])
        require(active_plugins(home) == [PACKAGE_NAMES["A"]], "A reinstall changed the selected plugin")

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

        print("[root-test] custom CODEX_HOME placement", flush=True)
        custom_home = base / "custom-home"
        custom_codex = base / "custom-codex"
        custom_env = dict(os.environ)
        custom_env["CODEX_HOME"] = str(custom_codex)
        run([shell, str(ROOT / "install.sh"), "--option", "A", "--archive-path", str(archive), "--home", str(custom_home), "--exclude-spark"], env=custom_env)
        require_install_layout(custom_home, custom_codex, "A")
        require(not (custom_home / ".codex").exists(), "custom CODEX_HOME install also wrote to the default home")
        project_config = custom_home / "project" / ".codex" / "ams-orchestration.toml"
        project_config.parent.mkdir(parents=True)
        project_config.write_text('schema_version = 1\nintensity = "minimal"\n', encoding="utf-8")
        run([shell, str(ROOT / "install.sh"), "--option", "UNINSTALL", "--home", str(custom_home), "--force"], env=custom_env)
        require(not custom_codex.joinpath("ams-orchestration.toml").exists(), "custom CODEX_HOME uninstall left managed config")
        require(project_config.exists(), "uninstall removed project-local configuration")

        print("[root-test] spaces, Unicode, nested, and long custom paths", flush=True)
        complex_home = base / "home with spaces" / "用户-Δ" / ("nested-" + "h" * 72)
        complex_codex = base / "codex with spaces" / "配置-λ" / ("nested-" + "c" * 72)
        complex_env = dict(os.environ)
        complex_env["CODEX_HOME"] = str(complex_codex)
        run([shell, str(ROOT / "install.sh"), "--option", "C", "--archive-path", str(archive), "--home", str(complex_home), "--exclude-spark"], env=complex_env)
        require_install_layout(complex_home, complex_codex, "C")
        require(not (complex_home / ".codex").exists(), "complex custom path wrote to the default Codex location")
        run([shell, str(ROOT / "install.sh"), "--option", "UNINSTALL", "--home", str(complex_home), "--force"], env=complex_env)
        require(not complex_codex.joinpath("ams-orchestration.toml").exists(), "complex custom path uninstall left managed config")

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
        second = run(
            [shell, str(ROOT / "install.sh"), "--option", "UNINSTALL", "--home", str(home), "--force"],
            env=offline_env,
        )
        require("No package-managed AMS installation was found" in second, "repeated root uninstall was not a local no-op")
        require(not curl_marker.exists(), "repeated root uninstall attempted a download")

        print("[root-test] complete archive rejection matrix", flush=True)
        test_archive_rejections(shell, archive, base)

        print("[root-test] symlinked local uninstaller rejection", flush=True)
        test_symlinked_uninstaller_rejection(shell, base)

        test_powershell_if_available(archive, base)

    print("ROOT INSTALLER TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
