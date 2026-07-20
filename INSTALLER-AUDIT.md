# Installer Audit

This audit covers only installation, update, package switching, configuration, validation, and uninstall tooling. Codex skill behavior and agent instructions are outside its scope.

## Audited components

- Root installers: `install.ps1` and `install.sh`
- Package PowerShell wrappers
- Python package installers
- Agent-profile installers
- Intensity configuration tools
- Package validators
- Installer unit and integration tests
- Package manifests

## Installation guarantees

The audited installer set now provides these guarantees:

1. **Explicit menu bypass** — Options A, B, C, and uninstall can be selected through command-line arguments, positional Bash arguments, or environment variables.
2. **Safe package switching** — Installing another option removes the previous active Adaptive Master–Subagent option instead of registering conflicting packages.
3. **Transactional writes** — Plugin directories, marketplace data, configuration, and managed profiles are staged or backed up and restored after a failed installation.
4. **Targeted rollback** — Rollback removes only package-managed files and does not delete unrelated or concurrently created user profiles.
5. **Strict package verification** — Manifests reject missing, changed, extra, duplicate, unsafe, linked, or generated-bytecode files.
6. **Safe ZIP extraction** — Root installers reject traversal, absolute paths, drive-prefixed paths, control characters, links, encrypted entries, duplicate names, excessive entry counts, and oversized expanded archives.
7. **Bounded execution** — Python subprocesses have hard timeouts and whole-process-tree cleanup, including the case where a direct child exits while a descendant retains captured output pipes.
8. **Cross-platform process handling** — Stale locks are recovered safely, Windows process checks avoid Unix-only signals, and Windows subprocesses are assigned to a kill-on-close Job Object when available.
9. **Atomic metadata updates** — Marketplace and configuration files are written through temporary files and replaced only after valid output is ready.
10. **Offline operation** — A local repository ZIP may be supplied, and uninstall uses the installed package without downloading another archive.
11. **Environment isolation** — Installer and validator Python processes run without user site initialization and do not generate package bytecode.
12. **Complete rollback reporting** — Failures restoring staged plugin backups are reported instead of being silently ignored.
13. **Reproducible line endings** — `.gitattributes` forces LF for repository text on every platform so shell parsing and package-manifest hashes cannot change during Windows checkout.
14. **Configuration ownership** — Package-created user configuration is marked and removed during uninstall; pre-existing unmarked user configuration is preserved.
15. **Idempotent root uninstall** — Root installers locate active or backed-up package uninstallers through canonical paths, work without downloading, and succeed when no package-managed installation remains.

## Validation coverage

The repository audit performs:

- Python syntax and import checks
- POSIX shell, Dash, and Bash syntax checks where available
- PowerShell parsing when a PowerShell runtime is available
- static PowerShell parameter, delimiter, strict-mode, and invocation checks otherwise
- reproducible LF and package-byte consistency checks
- root installer integration tests
- Option A, B, and C package validation
- install, update, switch, rollback, and uninstall tests
- strict manifest validation before and after tests
- lock and timeout regression tests
- unsafe archive and checksum rejection tests
- unrelated-file preservation tests
- generated-artifact checks
- repository-wide Markdown structure, readability, and local-link checks
- native Windows PowerShell installation, option switching, path-placement, and uninstall checks

Run the complete audit from the repository root:

```sh
python3 -B -E -s -S ./scripts/audit_installers.py
```

A successful run ends with:

```text
INSTALLER AUDIT PASSED
```

## Platform note

The release workflow runs the complete audit on both Ubuntu and Windows. Windows CI executes the PowerShell installer for Options A, B, and C, verifies package switching and file placement, and runs uninstall. Local systems without PowerShell still receive static PowerShell checks.
