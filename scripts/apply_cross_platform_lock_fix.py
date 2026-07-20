#!/usr/bin/env python3
"""Normalize non-file lock handling and regression coverage across all package options."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = (
    "adaptive-master-subagent-orchestration-option-a-two-skill",
    "adaptive-master-subagent-orchestration-option-b-unified",
    "adaptive-master-subagent-orchestration-option-c-installer-required",
)


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one match in {path}, found {count}: {old[:100]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


for package_name in PACKAGES:
    scripts = ROOT / package_name / "scripts"

    bootstrap = scripts / "bootstrap_profiles.py"
    replace_once(
        bootstrap,
        '''        except FileExistsError:
            try:
                metadata = lock_path.lstat()
                age = time.time() - metadata.st_mtime
            except FileNotFoundError:
                continue
            if not stat.S_ISREG(metadata.st_mode):
                raise SystemExit(f"Profile lock path is not a regular file: {lock_path}")
''',
        '''        except (FileExistsError, IsADirectoryError, PermissionError):
            try:
                metadata = lock_path.lstat()
                age = time.time() - metadata.st_mtime
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise SystemExit(f"Unable to inspect profile lock path {lock_path}: {exc}") from exc
            if not stat.S_ISREG(metadata.st_mode):
                raise SystemExit(f"Profile lock path is not a regular file: {lock_path}")
''',
    )

    intensity = scripts / "set_intensity.py"
    replace_once(
        intensity,
        '''        except FileExistsError:
            try:
                metadata = lock_path.lstat()
                age = time.time() - metadata.st_mtime
            except FileNotFoundError:
                continue
            if not stat.S_ISREG(metadata.st_mode):
                raise SystemExit(f"Intensity lock path is not a regular file: {lock_path}")
''',
        '''        except (FileExistsError, IsADirectoryError, PermissionError):
            try:
                metadata = lock_path.lstat()
                age = time.time() - metadata.st_mtime
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise SystemExit(f"Unable to inspect intensity lock path {lock_path}: {exc}") from exc
            if not stat.S_ISREG(metadata.st_mode):
                raise SystemExit(f"Intensity lock path is not a regular file: {lock_path}")
''',
    )

    installer = scripts / "install_package.py"
    replace_once(
        installer,
        '''        except FileExistsError:
            try:
                metadata = lock_path.lstat()
                age = time.time() - metadata.st_mtime
            except FileNotFoundError:
                continue
            if not stat.S_ISREG(metadata.st_mode):
                raise SystemExit(f"Install lock path is not a regular file: {lock_path}")
''',
        '''        except (FileExistsError, IsADirectoryError, PermissionError):
            try:
                metadata = lock_path.lstat()
                age = time.time() - metadata.st_mtime
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise SystemExit(f"Unable to inspect install lock path {lock_path}: {exc}") from exc
            if not stat.S_ISREG(metadata.st_mode):
                raise SystemExit(f"Install lock path is not a regular file: {lock_path}")
''',
    )

    test_intensity = scripts / "test_intensity.py"
    replace_once(
        test_intensity,
        '''        run("auto", env=env)
        require(not lock.exists(), "dead stale config lock was not cleared")
        require(tomllib.loads(config.read_text(encoding="utf-8"))["intensity"] == "auto", "stale-lock recovery did not update config")

        output = run("--dry-run", env=env, expect=2)
''',
        '''        run("auto", env=env)
        require(not lock.exists(), "dead stale config lock was not cleared")
        require(tomllib.loads(config.read_text(encoding="utf-8"))["intensity"] == "auto", "stale-lock recovery did not update config")

        lock.mkdir()
        output = run("heavy", env=env, expect=1)
        require("not a regular file" in output, "non-file intensity lock error was unclear")
        lock.rmdir()

        output = run("--dry-run", env=env, expect=2)
''',
    )

    test_install = scripts / "test_installation.py"
    replace_once(
        test_install,
        '''    lock.write_text(json.dumps({'pid':99999999,'host':socket.gethostname()})+'\\n',encoding='utf-8'); os.utime(lock,(old,old))
    run(home,'--exclude-spark'); require(not lock.exists(),'dead stale lock not removed')

def main()->int:
''',
        '''    lock.write_text(json.dumps({'pid':99999999,'host':socket.gethostname()})+'\\n',encoding='utf-8'); os.utime(lock,(old,old))
    run(home,'--exclude-spark'); require(not lock.exists(),'dead stale lock not removed')
    lock.mkdir()
    out=run(home,'--exclude-spark',expect=1); require('not a regular file' in out,'non-file install lock error was unclear')
    lock.rmdir()

def main()->int:
''',
    )

print("Cross-platform lock diagnostics and tests applied.")
