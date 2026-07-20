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


audit = ROOT / "scripts" / "audit_installers.py"
replace_once(
    audit,
    '''def markdown_audit() -> None:
    print("[audit] Markdown structure and links")
    run([sys.executable, "-B", "-E", "-s", "-S", str(ROOT / "scripts" / "audit_markdown.py")], timeout=60)
''',
    '''def manifest_inventory_audit() -> None:
    print("[audit] canonical package manifests")
    run([sys.executable, "-B", "-E", "-s", "-S", str(ROOT / "scripts" / "refresh_manifests.py"), "--check"], timeout=60)


def markdown_audit() -> None:
    print("[audit] Markdown structure and links")
    run([sys.executable, "-B", "-E", "-s", "-S", str(ROOT / "scripts" / "audit_markdown.py")], timeout=60)
''',
)
replace_once(
    audit,
    '''    no_generated_artifacts()
    markdown_audit()
''',
    '''    no_generated_artifacts()
    manifest_inventory_audit()
    markdown_audit()
''',
)

manual = ROOT / "MANUAL-INSTALLATION.md"
replace_once(
    manual,
    '''|-- install.ps1
|-- install.sh
|-- scripts/
|   |-- audit_installers.py
|   |-- audit_markdown.py
|   `-- process_utils.py
|-- tests/
|   `-- test_installers.py
''',
    '''|-- .gitattributes
|-- install.ps1
|-- install.sh
|-- scripts/
|   |-- audit_installers.py
|   |-- audit_markdown.py
|   |-- process_utils.py
|   `-- refresh_manifests.py
|-- tests/
|   |-- test_installers.py
|   `-- test_windows_installers.py
''',
)
replace_once(
    manual,
    '''The scripts-only audit checks manifests, plugin metadata, Python and shell syntax, profile installation, intensity handling, dry-runs, updates, option replacement, rollback, locks, timeouts, and uninstall behavior.
''',
    '''The scripts-only audit checks manifests, plugin metadata, Python and shell syntax, profile installation, intensity handling, dry-runs, updates, option replacement, rollback, locks, timeouts, and uninstall behavior.

After changing any packaged file, refresh all three manifests from the repository root:

```sh
python3 -B -E -s -S ./scripts/refresh_manifests.py
python3 -B -E -s -S ./scripts/refresh_manifests.py --check
```

The first command rewrites the manifests from the exact package bytes. The second verifies that no manifest is stale.
''',
)

installer_audit = ROOT / "INSTALLER-AUDIT.md"
replace_once(
    installer_audit,
    '''15. **Idempotent root uninstall** — Root installers locate active or backed-up package uninstallers through canonical paths, work without downloading, and succeed when no package-managed installation remains.
''',
    '''15. **Idempotent root uninstall** — Root installers locate active or backed-up package uninstallers through canonical paths, work without downloading, and succeed when no package-managed installation remains.
16. **Canonical manifest generation** — `scripts/refresh_manifests.py` regenerates every package manifest from the checked-out bytes and provides a non-mutating freshness check for CI.
''',
)
replace_once(
    installer_audit,
    '''- strict manifest validation before and after tests
''',
    '''- canonical manifest regeneration and freshness checks
- strict manifest validation before and after tests
''',
)

print("Canonical manifest audit and documentation wired.")
