# Installation

AMS 3.10 installs directly from canonical repository `main`. No release asset or package ZIP is used.

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

Installation ends when the installer completes. AMS performs no automatic follow-up verification or project pause.

## Exact installer scope

The installers use only:

```text
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install-manifest.txt
https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/adaptive-master-subagent-orchestration/...
```

They expose no repository-ref, manifest-URL, or raw-source environment override. Alternate sources require a separate explicit manual procedure.

They write only:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
$CODEX_HOME/agents/ams_*.toml
```

When `CODEX_HOME` is unset, profiles use `$HOME/.codex/agents/`. `AMS_SKILL_HOME` and `CODEX_HOME` may select destination roots. The installers do not edit `$CODEX_HOME/config.toml`, project settings, ACLs, or other Codex configuration.

## Verification and transaction

Both installers:

1. download `install-manifest.txt` from canonical `main`;
2. require `ams-install-manifest-v1`, version `3.10`, and the exact 33-file runtime/profile set;
3. reject malformed, duplicate, escaping, linked, redirected, oversized, or unexpected entries;
4. verify every downloaded file's byte length and SHA-256;
5. reread the manifest and require byte equality;
6. validate `VERSION = 3.10` and all 19 profile markers;
7. stage the complete skill before replacement;
8. transactionally install skill and eligible profiles with rollback;
9. leave byte-identical profiles unchanged;
10. upgrade only exact recognized prior official Spark profiles containing the former sandbox override;
11. refuse every other differing or ambiguous profile;
12. preserve settings, ineligible profiles, project-native state, unrelated skills, and unrelated files.

## Permission and authorization neutrality

All profiles inherit platform/user/project/work-order permissions and authorization boundaries. No current profile sets:

```text
sandbox_mode
approval policy
network access
writable roots
tool grants
credentials
target authority
authorization
```

The prior Spark hashes exist only so a direct user-authorized update can remove the former `workspace-write` override.

The Daybreak profile requests an optional account-gated access lane. Installation does not grant entitlement, target authorization, a provisioned workspace/API path, model attestation, retention treatment, or additional permission.

## Profile collision behavior

For each target profile:

- exact current bytes: unchanged;
- exact recognized prior official Spark bytes: backed up and upgraded;
- missing file: created;
- any other differing file: installation fails and rolls back without replacement.

A customized file remains untouched even if it has the managed marker. Review, rename, remove, or manually reconcile it before retrying.

## Installed source tree

```text
adaptive-master-subagent-orchestration/
├── SKILL.md
├── VERSION
├── agents/
│   └── openai.yaml
├── assets/
│   └── agent-profiles/
│       └── 19 canonical ams_*.toml profiles
└── references/
    ├── configuration-maintenance.md
    ├── daybreak-blue.md
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

Copy `adaptive-master-subagent-orchestration/` to `$HOME/.agents/skills/`, then copy all 19 profile files into `$CODEX_HOME/agents/`. Preserve exact permission-neutral bytes.

## Verify installation

### PowerShell

```powershell
$SkillRoot = Join-Path $HOME '.agents\skills\adaptive-master-subagent-orchestration'
$AgentRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'agents' } else { Join-Path $HOME '.codex\agents' }

Get-Content (Join-Path $SkillRoot 'VERSION')
Test-Path (Join-Path $SkillRoot 'references\project-governance.md')
Test-Path (Join-Path $SkillRoot 'references\configuration-maintenance.md')
Test-Path (Join-Path $SkillRoot 'references\root-execution-fallback.md')
Test-Path (Join-Path $SkillRoot 'references\daybreak-blue.md')
Test-Path (Join-Path $AgentRoot 'ams_daybreak_blue_max.toml')
(Get-ChildItem $AgentRoot -Filter 'ams_*.toml' -File).Count
Select-String -Path (Join-Path $AgentRoot 'ams_*.toml') -Pattern '^sandbox_mode\s*='
```

Expected: version `3.10`, all five path checks `True`, profile count `19`, and no `sandbox_mode` match.

### Bash

```bash
skill_root="$HOME/.agents/skills/adaptive-master-subagent-orchestration"
agent_root="${CODEX_HOME:-$HOME/.codex}/agents"

cat "$skill_root/VERSION"
test -f "$skill_root/references/project-governance.md"
test -f "$skill_root/references/configuration-maintenance.md"
test -f "$skill_root/references/root-execution-fallback.md"
test -f "$skill_root/references/daybreak-blue.md"
test -f "$agent_root/ams_daybreak_blue_max.toml"
find "$agent_root" -maxdepth 1 -type f -name 'ams_*.toml' | wc -l
! grep -R -n '^sandbox_mode[[:space:]]*=' "$agent_root"/ams_*.toml
```

## Daybreak fallback

Daybreak adds no setting. It is considered only after a qualifying standard-Sol cyber-safeguard refusal for one unchanged authorized defensive task.

Before task data or ownership is supplied, AMS:

1. establishes the normalized provisioned access path, compatible execution surface, approved identity/boundary, internal-only status, retention treatment, exact profile hash/model/effort, and a platform-observed or current-session root-generated signed-in Codex generation;
2. resolves one canonical root-owned route record shared by every fallback unit with that key;
3. serializes verification through a single reservation;
4. verifies capability for the exact unit using platform attestation, the current OpenAI onboarding validation workflow, or a distinguishing non-project synthetic defensive fixture;
5. requires universal `RESULT` plus `DAYBREAK CAPABILITY PREFLIGHT ADDENDUM`;
6. admits one task attempt only after unit-bound verification and immediate same-wave dispatch; interruption, compaction, handoff, root replacement, approval wait, or identity/path uncertainty before confirmed task start invalidates verification.

A nonce echo alone verifies transport, not Daybreak capability. Verification is not reusable across units or signed-in sessions. An authoritative failure closes the canonical record for every unit sharing the key. A route generation allows one initial verification start and one retry only after proof of a temporary no-start transport/capacity failure. The admitted task uses the same bounded process-start rule; a second no-start closes the route while leaving the task unit unstarted and blocked.

Daybreak is not ordinary routing, generic failure recovery, permission escalation, or automatic Red/Cyber/root escalation.

## Configuration updater and governance

`AMS CONFIGURATION UPDATE` and `AMS CONFIGURATION UPDATE PROJECT` update or create the project schema-2 file while preserving every existing value. Global values are consulted only when the project file is absent; an existing invalid global file blocks creation. `AMS CONFIGURATION UPDATE GLOBAL` adds missing defaults or creates the exact disabled default.

Project settings override global settings:

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

Unknown, duplicate, nested, invalid, or unsupported content remains an error.

```text
AMS GOVERNANCE off
```

disables only the optional project-governance layer. AMS never creates `.codex/ams-recovery.json`; continuity uses current root state, an authorized project-native system, or a user-visible handoff.

## Update and repair

Rerun the one-line installer. Exact prior official Spark profiles can be migrated. Any other differing profile blocks replacement. Do not bypass collision checks.

After an authorized installer completes, resume normal work. AMS performs no automatic package comparison, re-audit, activation check, project pause, or user-action request unless package-integrity verification is directly requested.

## Uninstall

Standard uninstall removes only:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
```

It preserves project/global settings and all installed profiles. Separate profile cleanup requires proven AMS ownership and explicit user authorization.
