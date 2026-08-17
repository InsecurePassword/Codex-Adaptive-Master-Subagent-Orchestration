# Adaptive Master–Subagent Orchestration

**Current release: 3.10**

Adaptive Master–Subagent Orchestration (AMS) is a Codex skill that keeps **GPT-5.6 Sol Max** in charge while routing bounded project work to the lowest-cost reliable non-root model and reasoning effort.

Its core rules are unchanged:

1. **Sol Max controls orchestration.** The root owns the objective, task graph, physical spawning, logical hierarchy, routing, integration decisions, acceptance, and user communication. Workers are leaves; delegated managers may request root-mediated descendants.
2. **AMS controls requested model and effort.** Every non-root dispatch uses an explicit AMS profile. Requested configuration is reported without claiming independently observed runtime identity.

Profiles do not grant sandbox, approval, network, writable-root, tool, credential, target, authorization, or other permission overrides.

## Install

The installers fetch the exact runtime/profile set from canonical repository `main` through `install-manifest.txt`. They do not use GitHub Release assets or a package ZIP.

### Windows PowerShell

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.ps1' | iex"
```

### Linux or macOS

```bash
curl -fsSL 'https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration/raw/refs/heads/main/install.sh' | bash
```

The installer writes only:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
$CODEX_HOME/agents/ams_*.toml
```

When `CODEX_HOME` is unset, profiles use `$HOME/.codex/agents/`. The installer does not edit `$CODEX_HOME/config.toml`, project settings, or operating-system permissions.

For a complete source copy:

```bash
git clone https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration.git
```

See [INSTALLATION.md](INSTALLATION.md) for validation, profile-collision, repair, and uninstall behavior.

## Persistence and settings

AMS checks project settings first, then global settings only when the project file is absent:

```text
<project-root>/.codex/ams-orchestration.toml
$CODEX_HOME/ams-orchestration.toml
```

Project and global files are not merged. Global configuration is never written implicitly. Normal controls write only the project file; `AMS CONFIGURATION UPDATE GLOBAL` only adds missing defaults or creates the exact disabled default.

Schema 2 remains unchanged:

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

Daybreak Blue adds no setting or schema migration. Omitted supported fields resolve from the current default and are persisted on the next authorized write. Unknown, duplicate, nested, invalid, or unsupported content remains an error.

Useful commands:

```text
AMS STATUS
AMS ENABLE
AMS DISABLE
AMS MODE auto|minimal|balanced|moderate|heavy|extreme
AMS IMPLICIT on|off
AMS GOVERNANCE on|off
AMS ROOT FALLBACK on|off
AMS CONFIGURATION UPDATE [PROJECT|GLOBAL]
AMS SPARK on|off
AMS SPARK RECHECK
AMS SPARK EFFORTS low,medium,high
AMS PROFILES auto|installer
```

## Optional project governance

`project_governance = true` adds project-wide acceptance tracking, proportional independent review, continuous-delivery posture, deviation handling, and continuity through existing project-native state or a user-visible handoff.

```text
AMS GOVERNANCE off
```

Disabling governance does not change root authority, model/effort routing, work orders, hierarchy, one-writer safety, or truthful completion.

## Model and effort routing

| Family or lane | Typical work |
|---|---|
| **Spark** | Exact commands, searches, extraction, routine tests/builds, formatting, and bounded mechanics. Worker-only. |
| **Luna** | Clear, repetitive, low-risk work that is easy to verify. |
| **Terra** | Normal implementation, fixes, tests, documentation, review, and moderate investigation. |
| **Sol** | Architecture, security-sensitive work, ambiguity, difficult debugging, and expensive-to-fail decisions. |
| **Daybreak Blue** | Refusal-triggered worker-only fallback for one unchanged authorized defensive cybersecurity task. Never normal routing. |

Sol, Terra, and Luna support `low`, `medium`, `high`, `xhigh`, and `max`; Spark supports `low`, `medium`, and `high`. Daybreak has one profile: `ams_daybreak_blue_max`.

After a successful spawn AMS reports the requested profile, for example:

```text
semantic_reviewer started: ams_sol_xhigh
```

That is routing evidence, not proof of observed runtime identity.

## Daybreak Blue

Daybreak Blue is an optional lane for approved defensive cybersecurity work through OpenAI Daybreak and Trusted Access for Cyber. Installing AMS only installs the profile. It does not request, provision, transfer, or prove access.

### Activation

AMS first routes security-sensitive work to standard Sol. Daybreak is considered only when:

- the task is lawful, authorized defensive work on a system, codebase, artifact, account, network, or data the user owns, operates, or is explicitly authorized to analyze;
- the Sol root received an explicit cyber-safeguard refusal during root handling or from a standard Sol `worker` or `delegated-manager`;
- the bounded task remains required;
- target, scope, exclusions, authority, permissions, data boundary, and operational effect remain unchanged;
- no higher-priority safety, authorization, ownership, project-native, or Trusted Access/data-governance control blocks it.

Weak or partial output, ordinary inability, timeout, missing tools/context, sandbox/approval denial, network restriction, quota/account error, unsupported effort, or non-cyber refusal does not qualify.

AMS assigns one stable fallback-unit ID to the frozen task. Equivalent refusals, retries, replacements, replication, resumed work, and reparenting map to the same unit. Its **task-attempt** state is:

```text
not-started | active | consumed
```

Extreme and Zergling Rush cannot duplicate the unit or increase its one task attempt.

### Canonical access-route record

Access state is not copied into each fallback unit. The root owns one canonical route record for each normalized combination of:

- provisioned access path and execution surface;
- approved identity and organization/workspace/API-project boundary;
- internal-only and retention treatment;
- exact Daybreak profile hash, model, and effort;
- current signed-in Codex session generation.

The route record is:

```text
unverified | verifying | verified | closed-unavailable
```

Only one unit may reserve and verify/use a route record at a time. Verification is bound to that exact unit, logical parent, custody state, intensity shape, root objective, and session generation. It is never reused across units or signed-in sessions. After the admitted task terminates, the route returns to `unverified` unless authoritative evidence closes it.

`closed-unavailable` applies to every unit sharing the route key and survives replacement, reparenting, compaction, handoff, root replacement, and recovery. It reopens only through a new generation after explicit new provisioning evidence or an explicit user-directed recheck following a material access change. Late results cannot overwrite a newer generation or reopen a closed route.

### Provisioned access path

Before verification, AMS records a non-secret access context:

```text
Provisioned access path: codex-workspace | api-organization | user-or-model-specific
Execution surface: codex-interactive | codex-security-plugin | codex-cli | codex-github-action | responses-api | approved-codex-api-workflow | exact-provisioned-surface
Approved identity or membership basis:
Approved organization/workspace/project boundary:
Internal-only use confirmed: yes
Retention requirement and coverage:
Provisioning and retention evidence IDs:
Signed-in session generation ID:
```

Compatibility is strict:

- `codex-workspace` may use only a Codex surface explicitly covered by the named internal Codex/ChatGPT organization or workspace.
- `api-organization` may use only the Responses API or an explicitly approved Codex API workflow authenticated to the named internal API organization/project.
- `user-or-model-specific` may use only the exact surface named by OpenAI; `none-user-level` is valid only when provisioning explicitly states that no organization/workspace/project applies.
- Workspace and API approval are separate route records and are never combined.

A profile, installation, model catalog entry, prior session, or absence of an error is not proof. If the exact path, surface, identity, boundary, internal-only status, signed-in session generation, or required retention coverage cannot be established, AMS stops before verification or task data.

### Capability-verification preflight

Before project ownership or task data is sent, the exact unit must reserve the canonical route and pass a non-project capability preflight through `ams_daybreak_blue_max`.

The preflight receives no project files, repository content, telemetry, malware samples, credentials, secrets, customer data, refusal excerpt, target details, project ownership, Git authority, mutation authority, network collection authority, or live-target interaction.

Capability proof must use one of:

1. platform-attested effective Daybreak identity;
2. the current bounded defensive validation workflow supplied through OpenAI onboarding;
3. a public or organization-approved, local-only synthetic defensive fixture with explicit expected results, where the identical fixture first produced a qualifying standard-Sol safeguard refusal in the current session.

A synthetic fixture may use inert toy code or static artifacts for defensive analysis. It may not contain user/customer data, a live target, credentials, a working malware payload, persistence/stealth, an exploit chain, external side effects, or deployment instructions.

A nonce protects against replay, but a nonce echo alone proves transport and does not establish Daybreak capability. The verification session returns the universal AMS `RESULT` plus `DAYBREAK CAPABILITY PREFLIGHT ADDENDUM`, including fixture/control evidence, expected-result status, route generation, unit binding, role confirmation, and no-data/no-mutation confirmation.

Only a fully validated result sets the route to `verified`.

### Verification retry budget

Each route generation permits:

1. one initial Daybreak verification process-start attempt;
2. one retry only when the first failure is proven to have occurred before any Daybreak session started and was a temporary transport or capacity failure.

A confirmed or uncertain start, malformed or non-distinguishing result, failed capability criterion, refusal, substitution, mismatch, entitlement/access failure, wrong context, or second no-start failure closes the route without automatic retry. A material provisioning/access change requires explicit evidence and a new route generation.

### Task attempt and data handling

After verification, AMS rechecks the unit binding, current profile hash, access context, custody, ownership, and task state. It then sends only the minimized data needed for the unchanged defensive task.

A confirmed task start changes the unit to `active`. Every terminal outcome after confirmed start changes it to `consumed`. An uncertain start remains `active` until closure is proven. AMS does not repeat, fan out, rotate profiles, reset through reparenting/recovery, or automatically escalate to Daybreak Red, GPT-5.6 Cyber, an offensive workflow, or root execution.

The worker inherits the same sandbox, approval, network, tool, writable-root, ownership, logical-parent, and Git-authority boundaries as the refused route. Daybreak does not grant broader access, credentials, collection authority, or target authority.

Capability verification and task sessions return normal `RESULT` plus the applicable Daybreak addendum. Physical delivery to the root is transport; task evidence is reconciled through the logical parent or explicit superseding custodian.

AMS creates no Daybreak cache, transcript service, external uploader, or recovery ledger. Durable state uses an existing authorized project-native record or user-visible handoff. Data remains subject to the exact approved surface's controls and retention terms.

### Trusted Access required

The active account must already have approved Daybreak/Trusted Access on the exact internal path and surface used by AMS. OpenAI approval is not automatic and may apply to a Codex/ChatGPT organization or workspace, an API organization, or both as separately provisioned paths.

Trusted Access is internal-only. It may not be resold, proxied, exposed to external users, used for customer-facing traffic, or treated as target authorization. It does not remove all safeguards, guarantee every cyber model, include Daybreak Red, or include Zero Data Retention automatically. ZDR/custom retention must be separately confirmed for the exact organization/project and surface.

Current onboarding references:

- [OpenAI Daybreak — Trusted Access for Cyber Overview](https://help.openai.com/en/articles/20001258-openai-daybreak-trusted-access-for-cyber-overview)
- [Enterprise Daybreak onboarding](https://help.openai.com/en/articles/20001261-enterprise-daybreak-onboarding)

## Virtual hierarchy and root boundary

- The root is the sole physical spawn authority.
- Workers never delegate.
- Delegated managers request descendants through the root.
- Spark and Daybreak are always workers.
- Every non-root session has an immutable logical parent.
- One active writer is allowed per mutable surface.
- Only the root accepts project completion and communicates with the user.
- The root remains management while a compliant delegated route exists.

Under `minimal`, a refusing manager records the Daybreak request, relinquishes ownership, and closes. Any required standard-Sol control, capability verification, and task run serially as the only active non-root session while retaining the inactive manager order as logical parent. The manager is resumed or superseded afterward for reconciliation.

## Root execution fallback

`root_execution_fallback = true` permits only the bounded last-resort behavior in `root-execution-fallback.md`. It does not create a routine root lane.

```text
AMS ROOT FALLBACK off
```

An unavailable or exhausted Daybreak route never authorizes the root to execute the refused cybersecurity task.

## Configuration maintenance

```text
AMS CONFIGURATION UPDATE
AMS CONFIGURATION UPDATE PROJECT
AMS CONFIGURATION UPDATE GLOBAL
```

Project forms preserve existing values and add missing current fields. A missing project file may use valid global values. An invalid global file blocks project creation rather than being ignored. The explicit global form adds missing defaults or creates the exact disabled default. No form changes an existing value or enables AMS.

## Intensity modes

| Mode | Posture |
|---|---|
| `minimal` | Root plus at most one active non-root session. |
| `balanced` | One small bounded direct-worker or manager team shape. |
| `auto` | Smallest useful adaptive topology. |
| `heavy` | Useful managers and parallel lanes. |
| `extreme` | Every useful ready safe lane while remaining cost-first. |

`moderate` remains the schema-2 alias for `balanced`.

## Zergling Rush

Zergling Rush is a separate explicit-consent mode that may use stronger models, duplicate investigation, speculative preparation, and redundant validation. It never changes authority, permissions, ownership, safety, or completion. It cannot proactively select Daybreak, duplicate a fallback unit, bypass verification, reopen a closed route, or increase verification/task budgets.

## Profile and installer safety

The installer deploys 19 profiles. Byte-identical profiles are unchanged. Exact recognized prior official Spark profiles may be upgraded to remove their former sandbox override. Any other differing, customized, marker-only, malformed, or user-authored profile is preserved and blocks replacement.

Installer validation runs only inside an explicitly invoked installer. After completion AMS performs no automatic package comparison, re-audit, project pause, or user gate unless package-integrity verification is directly requested.

Standard uninstall removes only the skill directory and preserves settings and profiles.

## Requirements

- Codex with skills and custom-subagent support
- a top-level GPT-5.6 Sol Max session, or verified equivalent Sol alias at Max reasoning
- approved Daybreak access on the exact internal provisioned path and surface when the optional fallback is needed
- Windows PowerShell 5.1+ for the PowerShell installer
- Bash plus `curl`, `awk`, `sort`, `cmp`, `mktemp`, `wc`, `tr`, `grep`, `head`, `tail`, `od`, `find`, `dirname`, and either `sha256sum` or `shasum`
