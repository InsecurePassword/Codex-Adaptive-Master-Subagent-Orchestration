# Installation

AMS 3.09 installs directly from the canonical repository `main` tree. No release asset or package ZIP is used.

## One-line installation

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.ps1' | iex"
```

Requirements: Windows PowerShell 5.1 or newer and built-in .NET/PowerShell components.

### Linux or macOS

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.sh' | bash
```

Requirements: Bash; `curl`, `awk`, `sort`, `cmp`, `mktemp`, `wc`, `tr`, `grep`, `head`, `tail`, `od`, `find`, `dirname`; and either `sha256sum` or `shasum`.

Installation does not trigger AMS re-verification, reactivation, or a project pause. Ordinary runtime reads installed references only when they are later needed.

## Exact installer scope

The standard installers use only these canonical URLs:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install-manifest.txt
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/adaptive-master-subagent-orchestration/...
```

They expose no environment-variable override for repository ref, manifest URL, or raw source. Alternate sources require a separate explicit manual procedure.

The installers write only:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
$CODEX_HOME/agents/ams_*.toml
```

When `CODEX_HOME` is unset, profiles use `$HOME/.codex/agents/`. `AMS_SKILL_HOME` and `CODEX_HOME` may select destination roots. The installers do not edit `$CODEX_HOME/config.toml`, project `.codex/ams-orchestration.toml`, operating-system ACLs, or other Codex configuration.

## Verification and transaction

Both installers:

1. download `install-manifest.txt` from canonical `main`;
2. require manifest format `ams-install-manifest-v1`, version `3.09`, and the exact 31-file runtime/profile set;
3. reject malformed, duplicate, escaping, linked, redirected, oversized, or unexpected entries;
4. download every declared file and verify byte length and SHA-256;
5. download the manifest again and require byte equality, preventing mixed-generation installation;
6. validate `VERSION = 3.09` and all 18 bundled profile markers;
7. stage the complete skill before replacement;
8. transactionally install the skill and eligible profiles with rollback;
9. leave byte-identical profiles unchanged;
10. upgrade only exact installer-recognized prior official Spark profiles that contained the former sandbox override;
11. refuse every other differing or ambiguous profile instead of trusting a marker alone;
12. preserve project/global settings, installed profiles not eligible for replacement, project-native state, unrelated skills, and unrelated files.

## Permission neutrality

All installed profiles inherit platform/user/work-order permissions. No current profile sets:

```text
sandbox_mode
approval policy
network access
writable roots
tool grants
```

The previous public Spark profile hashes are recognized only so a direct user-authorized reinstall/update can remove their former `workspace-write` override safely.

## Profile collision behavior

For each target profile:

- exact current bytes: unchanged;
- exact recognized prior official Spark bytes: backed up and upgraded;
- missing file: created;
- any other differing file: installation fails and rolls back without replacing it.

A customized file remains untouched even when its first line contains the AMS managed marker. Review, rename, remove, or manually reconcile it before retrying.

## Installed source tree

```text
adaptive-master-subagent-orchestration/
├── SKILL.md
├── VERSION
├── agents/
│   └── openai.yaml
├── assets/
│   └── agent-profiles/
│       └── 18 canonical ams_*.toml profiles
└── references/
    ├── configuration-maintenance.md
    ├── hierarchy-control.md
    ├── intensity-control.md
    ├── package-maintenance.md
    ├── profile-management.md
    ├── project-control.md
    ├── project-governance.md
    ├── root-execution-fallback.md
    ├── runtime-core.md
    └── zergling-rush.md
```

## Manual installation with Git

```bash
git clone https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration.git
cd Codex-Adaptive-Master-Subagent-Orchestration
```

Copy `adaptive-master-subagent-orchestration/` to `$HOME/.agents/skills/`, then copy all 18 files under `assets/agent-profiles/` into `$CODEX_HOME/agents/`. Manual installation must preserve the same permission-neutral profile bytes.

## Verify installation

### PowerShell

```powershell
$SkillRoot = Join-Path $HOME '.agents\skills\adaptive-master-subagent-orchestration'
$AgentRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'agents' } else { Join-Path $HOME '.codex\agents' }

Get-Content (Join-Path $SkillRoot 'VERSION')
Test-Path (Join-Path $SkillRoot 'references\project-governance.md')
Test-Path (Join-Path $SkillRoot 'references\configuration-maintenance.md')
Test-Path (Join-Path $SkillRoot 'references\root-execution-fallback.md')
(Get-ChildItem $AgentRoot -Filter 'ams_*.toml' -File).Count
Select-String -Path (Join-Path $AgentRoot 'ams_spark_*.toml') -Pattern '^sandbox_mode\s*='
```

Expected: version `3.09`, all three reference checks `True`, profile count `18`, and no `sandbox_mode` matches.

### Bash

```bash
skill_root="$HOME/.agents/skills/adaptive-master-subagent-orchestration"
agent_root="${CODEX_HOME:-$HOME/.codex}/agents"

cat "$skill_root/VERSION"
test -f "$skill_root/references/project-governance.md"
test -f "$skill_root/references/configuration-maintenance.md"
test -f "$skill_root/references/root-execution-fallback.md"
find "$agent_root" -maxdepth 1 -type f -name 'ams_*.toml' | wc -l
! grep -R -n '^sandbox_mode[[:space:]]*=' "$agent_root"/ams_spark_*.toml
```

## Root fallback and configuration updater

The schema-2 default includes `root_execution_fallback = true`. `AMS ROOT FALLBACK on|off` changes only the project fallback setting.

`AMS CONFIGURATION UPDATE` and `AMS CONFIGURATION UPDATE PROJECT` update an existing project configuration as well as creating a missing one. Existing project values are preserved and every missing current field is added from the exact default. Global values are consulted only when the project file is absent; an existing invalid or unsafe global file blocks creation rather than being ignored. `AMS CONFIGURATION UPDATE GLOBAL` is the sole explicit AMS command allowed to write the global file and only adds missing defaults or creates the exact disabled default.

## Settings and governance

Project settings override global settings. A project-setting command creates an absent project file from current valid global values when available, then changes only the requested key.

```toml
schema_version = 2
enabled = false
allow_implicit_invocation = true
intensity = "auto"
project_governance = true
root_execution_fallback = true
spark_enabled = true
spark_available = true
spark_efforts = ["low", "medium", "high"]
profile_management = "auto"
```

Any omitted currently supported schema-2 setting resolves from the exact current default and is written during the next authorized settings change. Unknown, duplicate, nested, invalid, or unsupported content remains an error.

Disable only the optional project-governance layer with:

```text
AMS GOVERNANCE off
```

AMS does not create `.codex/ams-recovery.json`. Live orchestration state remains in the root session; durable continuity uses an existing authorized project-native system or a user-visible handoff.

## Update and repair

Rerun the appropriate one-line installer. A normal update safely migrates exact prior official Spark profiles. Any other differing profile blocks replacement and is reported precisely. Do not bypass the collision check.

During an explicitly requested update, AMS quiesces package writers and the installer performs the required manifest and hash validation. After success, do not compare pre/post package state, run post-update hashes, re-verify, re-audit, reactivate, pause the project, or request user action solely because the package changed. Resume ordinary AMS operation; references are read normally only when later needed. A user may separately request package-integrity verification.

## Uninstall

Standard uninstall removes only:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

It intentionally preserves project/global settings and all installed profiles for troubleshooting or reinstall. Remove profiles separately only after proving exact AMS ownership and receiving explicit user authorization.
