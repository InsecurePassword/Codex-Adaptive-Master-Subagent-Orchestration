# Installation

AMS 4.0 installs from canonical published `main`. The standard installer uses no Release asset or package ZIP.

## One-line installation

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.ps1' | iex"
```

Requirements: Windows PowerShell 5.1+ and built-in .NET/PowerShell components.

### Linux or macOS

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.sh' | bash
```

Requirements: Bash; `curl`, `awk`, `sort`, `cmp`, `mktemp`, `wc`, `tr`, `grep`, `head`, `tail`, `od`, `find`, `dirname`, `iconv`; and either `sha256sum` or `shasum`.

Installation ends when the installer completes. AMS performs no automatic follow-up audit or project pause.

## Transaction and runtime preservation

Both installers:

1. acquire the shared package/runtime lock used by convergence record writers;
2. download canonical `install-manifest.txt` and require version `4.0` plus the exact core file set;
3. reject malformed, duplicate, escaping, linked, redirected, oversized, or unexpected entries;
4. verify every length/SHA-256 and require a byte-identical second manifest read;
5. validate `VERSION = 4.0` and all 18 profile markers;
6. validate the exact bounded convergence runtime layout and record format when present;
7. stage the complete skill, preserve an exact runtime snapshot, and install transactionally with rollback;
8. leave byte-identical profiles unchanged and refuse unrecognized differing profiles;
9. hold the shared lock through runtime restoration and backup deletion;
10. preserve project/global configuration and unrelated files/profiles.

Package-local `.runtime` is user/runtime state, not a manifest member. Safe runtime state consists only of bounded convergence tracking records and immutable history records under `adaptive-master-subagent-orchestration/.runtime/convergence/`. Unsafe state blocks replacement rather than being copied.

## Installed core tree

```text
adaptive-master-subagent-orchestration/
├── SKILL.md
├── VERSION
├── agents/openai.yaml
├── assets/agent-profiles/        # 18 canonical profiles
└── references/                   # core and lazy contracts
```

The core contains no Python requirement or runtime test framework.

## Configuration

The exact master contract is normative in `adaptive-master-subagent-orchestration/references/project-control.md`.

- Missing supported fields use current defaults.
- Unknown fields fail closed.
- Retired top-level `schema_version` is ignored and removed on the next authorized write.
- Project settings completely override global settings.
- Settings survive install/update/uninstall/reinstall unless explicitly changed.
- `AMS CONFIGURATION UPDATE [PROJECT|GLOBAL]` completes missing current fields without changing existing supported values.

## Optional companions

The standard installer does not install companions. Copy a required directory from `extensions/` into `$HOME/.agents/skills/` and verify `COMPATIBILITY` is `4.0`:

```text
extensions/ams-app-task-lane/
extensions/ams-runtime-observation/
```

Installing a companion does not enable it. Its core feature setting/override and operational trigger remain required; implicit invocation is disabled. The runtime-observation companion optionally requires Python 3.11+ or Windows PowerShell 5.1+.

## Manual core installation

Clone the repository, copy `adaptive-master-subagent-orchestration/` to `$HOME/.agents/skills/`, and copy all 18 profiles into `$CODEX_HOME/agents/` (or `$HOME/.codex/agents/`). Preserve safe `.runtime` only under the shared package/runtime lock.

## Update and repair

Rerun the appropriate installer. It acquires the shared lock, validates and preserves runtime state, stages the complete candidate, and rolls back on failure.

## Supported downgrade preparation

Older installers may delete AMS 4.0 package-local convergence state. Before an authorized downgrade:

1. stop convergence record mutation at a safe boundary;
2. acquire `<skill-parent>/.adaptive-master-subagent-orchestration.runtime.lock`;
3. validate and copy `<skill-root>/.runtime/convergence/` to a user-selected directory outside the skill root, preferably `$CODEX_HOME/ams-runtime-export/<UTC-id>/`;
4. record each relative path, byte length, and SHA-256;
5. release the lock, then run the older installer.

An older release cannot be assumed to resume the exported records. Reimport only after reinstalling a compatible AMS version, under its shared lock, after validating the export and proving no conflicting active state. A direct downgrade without export may destroy convergence history and must be disclosed before execution.

## Uninstall

Standard uninstall preserves project/global configuration and installed profiles unless separately authorized. Before removing the skill root, preserve package-local convergence records in place when supported or export them using the downgrade procedure. Remove runtime history only with explicit full-runtime-cleanup authority.

Repository release-verification utilities are outside the install manifest, are never installed as AMS core, and are never executed during project orchestration.
