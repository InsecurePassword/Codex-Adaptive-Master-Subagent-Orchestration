# Product Documentation

**Product:** Adaptive Master–Subagent Orchestration (AMS)  
**Release:** 3.10

## 1. Product boundary

AMS keeps a GPT-5.6 Sol Max root, or verified equivalent Sol alias at Max reasoning, in control of the objective, task graph, physical dispatch, logical hierarchy, model/effort selection, ownership, integration, acceptance, and user communication. Bounded non-root sessions perform project work. Workers never delegate; delegated managers may request root-mediated descendants but never physically spawn or expand authority.

Every dispatch uses an explicit AMS profile. A requested profile is routing evidence, not independent attestation of the effective runtime identity.

## 2. Installed components and side effects

The standard installer writes only:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
$CODEX_HOME/agents/ams_*.toml
```

It installs 19 profiles, does not edit `$CODEX_HOME/config.toml`, project settings, ACLs, or general Codex permissions, and leaves profiles after standard uninstall. AMS may create `<project-root>/.codex/ams-orchestration.toml` only under the control-file rules. It never creates an AMS recovery file.

## 3. Installation and trust

The canonical installers fetch `install-manifest.txt` and its exact 33-file set from repository `main`, verify byte lengths and SHA-256 values, reread the manifest for equality, stage the full package, and install transactionally with profile rollback. See [INSTALLATION.md](INSTALLATION.md).

## 4. Settings and precedence

Project settings override global settings completely; files are not merged:

```text
<project-root>/.codex/ams-orchestration.toml
$CODEX_HOME/ams-orchestration.toml
```

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

Daybreak Blue adds no setting, status field, availability cache, or schema migration. Unknown, duplicate, nested, invalid, or unsupported settings remain errors.

## 5. Commands

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

Normal controls write only the project file. `AMS STATUS` is read-only. `AMS CONFIGURATION UPDATE GLOBAL` is the sole global-writing command and never changes an existing value or enables AMS.

## 6. Model and reasoning control

```text
ams_<sol|terra|luna>_<low|medium|high|xhigh|max>
ams_spark_<low|medium|high>
ams_daybreak_blue_max
```

| Route | Intended work |
|---|---|
| Spark | Bounded mechanics requiring little judgment; worker-only. |
| Luna | Explicit repetitive low-risk work. |
| Terra | Normal implementation, tests, documentation, review, and investigation. |
| Sol | Ambiguous, architectural, security-sensitive, difficult, or expensive-to-fail work. |
| Daybreak Blue | Worker-only fallback for one unchanged authorized defensive cyber task explicitly refused by standard Sol for cyber-safeguard reasons. |

Daybreak Blue has only `max` because it is an access-path fallback, not a cost tier.

### 6.1 Daybreak trigger and frozen unit

Daybreak is never proactive. It is considered only after an explicit qualifying cyber-safeguard refusal during root handling or from a standard Sol `worker` or `delegated-manager`, when the still-required task is authorized defensive work and its target, scope, exclusions, authority, data boundary, permissions, and operational effect remain unchanged.

Generic failure, weak output, timeout, missing context or tools, sandbox/approval denial, network restriction, account/quota failure, unsupported effort, or non-cyber refusal is not a trigger.

The root assigns one stable `Daybreak fallback unit ID` to the frozen task. Equivalent refusals, retries, replacements, resumed work, replication, and reparenting map to the same unit.

Task-attempt state and route availability are independent:

```text
Attempt state: not-started | active | consumed
Route disposition: unverified | verifying | verified | closed-unavailable
Access-context ID:
Route-evidence ID:
Route blocker:
Reopen condition:
```

`closed-unavailable` survives recovery and may reopen only after explicit new provisioning evidence or a user-directed recheck following a material access-context change.

### 6.2 Trusted Access and data-governance gate

Before any Daybreak worker is started, the root records a non-secret context for the active surface:

```text
Trusted Access scope: user-level | named workspace | API organization/project
Approved identity or membership basis:
Approved organization/workspace/project:
Approved product surface: Codex
Internal-only use confirmed: yes
Retention requirement: standard approved-surface terms | ZDR | custom
Retention coverage: confirmed | not-required-beyond-standard
Retention evidence ID:
Provisioning/onboarding evidence ID:
Access-context ID:
```

The evidence may be platform-observed metadata, an approved onboarding record, or explicit current user confirmation tied to the signed-in identity and surface. A profile, installation, model catalog, prior session, or absence of an error is not proof. If identity, approved organization/workspace/project, Codex surface, internal-only status, or required retention coverage cannot be established, fail closed before sending task data.

### 6.3 Mandatory data-free access preflight

A task attempt requires `Route disposition = verified`. Otherwise, after the qualifying refusal, the root dispatches one nonce-bound `access-preflight` through `ams_daybreak_blue_max` using the planned logical parent and access context.

The preflight receives no project files, repository content, telemetry, malware, credentials, secrets, customer data, refusal excerpt, target details, project ownership, Git authority, or mutation permission. It performs no project inspection, command execution, target interaction, or data collection. It does not consume the one task-attempt budget.

It must return the same verification ID and nonce, confirm `worker/none`, confirm no project data access or mutation, and prove the result-return path. Only then does the root set the route to `verified`. A malformed receipt, unsupported model/effort, explicit mismatch, entitlement/access-path failure, wrong context, or uncertain preflight start/result sets `closed-unavailable` and prohibits automatic retry.

The preflight proves requested Codex custom-agent routing for the exact context; it is not independent model attestation when effective identity is hidden.

### 6.4 Lineage, intensity, and ownership

Daybreak workers are physical root children but retain the correct logical parent.

- Root-handling refusal: logical parent `root`.
- Refused Sol worker: close/supersede it, prove it non-live, and preserve its logical parent.
- Refusing Sol delegated manager in `balanced`, `heavy`, `extreme`, or Rush: manager remains logical parent, relinquishes the affected execution surface, and does not write concurrently.
- Refusing delegated manager in `minimal`: manager records the request, relinquishes ownership, reaches a boundary, and closes; preflight and task run serially as the only active non-root sessions while retaining the inactive manager order as logical parent; after task closure, resume that manager or issue a superseding manager order for reconciliation.
- Genuinely unavailable parent or deliberate flattening: use the established hierarchy supersession and custody-transfer procedure.

Every Daybreak worker consumes one ordinary worker slot while active. One-writer safety and finite allocation remain mandatory.

### 6.5 Task attempt, evidence, and completion

After a successful preflight, the task work order carries the verified access-context ID and evidence, refusal provenance, frozen task/data boundary, ownership/custody transfer, minimized required data, requested route, and one-attempt budget.

A confirmed task start sets `active`. Every terminal outcome after confirmed start sets `consumed`. An uncertain start remains `active` until closure is proved. AMS does not repeat, fan out, rotate, or reset the task because of replacement, reparenting, recovery, Extreme, or Rush. It never automatically escalates to Daybreak Red, GPT-5.6 Cyber, an offensive workflow, or root execution.

The worker returns normal `RESULT` plus `DAYBREAK RESULT ADDENDUM`. Physical delivery to the root is transport; evidence is reconciled through the recorded logical parent or explicit superseding custodian. Daybreak output is evidence, not project acceptance.

## 7. Permission and data neutrality

Profiles grant no sandbox, approval, network, writable-root, tool, credential, target, or authorization privilege. Daybreak uses the same inherited platform/user/project/work-order controls as other routes.

No task data is sent during preflight. After verification, the task receives only the frozen objective, minimal relevant code/artifacts/telemetry, bounded refusal evidence, and authorization basis. AMS creates no Daybreak cache, transcript service, external uploader, or recovery ledger. Data remains subject to the exact approved surface's controls and retention terms; Trusted Access and ZDR/custom retention are separate provisioning decisions.

## 8. Profile installation and repair

Existing profiles are handled strictly:

- exact current bytes: unchanged;
- exact recognized prior official Spark bytes: upgraded during authorized install/update;
- missing profile: created;
- any other differing profile: preserved and blocks replacement.

Runtime `profile_management = "auto"` may create a selected missing profile only. It cannot overwrite a differing profile or repair Daybreak access by changing credentials, workspaces, permissions, product surfaces, or retention controls.

## 9. Root authority and work orders

Valid role/authority pairs are `worker/none` and `delegated-manager/request`. The root alone physically spawns, owns global routing and task state, accepts results, declares completion, and communicates with the user. Every non-root order has one immutable logical parent. Daybreak preflight and task orders have distinct work-order IDs but share the same stable fallback unit and access context.

## 10. Virtual hierarchy and ownership

All sessions may remain physical root children while work-order lineage records logical parentage. Authority, permissions, scope, ownership, and allocation may narrow but never expand. One active writer is allowed per mutable surface. Results must pass through the logical parent before root acceptance.

## 11. Root execution boundary

The root is a management lane and does not perform project inspection, research, implementation, commands, deployment, tests/builds/linting, security checks, independent review, Git/history operations, or artifact generation while a compliant delegated route exists.

## 12. Root execution fallback

Root fallback remains a bounded, low-risk, reversible last-resort unblocker and is ineligible for security-sensitive execution. An unavailable or exhausted Daybreak route does not authorize the root to perform the refused cyber task.

## 13. Configuration maintenance

The explicit updater preserves all existing supported values, adds only missing defaults, rejects invalid content, and never runs implicitly. A missing project file may inherit valid global values; `AMS CONFIGURATION UPDATE GLOBAL` may create only the exact disabled global default.

## 14. Intensity and Rush

`minimal`, `balanced`, `auto`, `heavy`, and `extreme` change team formation, not quality, safety, ownership, or completion authority. Zergling Rush requires explicit current-turn consent. Neither Extreme nor Rush makes Daybreak proactive, duplicates a fallback unit, bypasses preflight, reopens a closed route, or increases the task-attempt budget.

## 15. Optional project governance

When enabled, project governance adds lifecycle tracking, proportional validation/review, deviation handling, and continuity through existing project-native state or a user-visible handoff. It does not change core authority or Daybreak gates.

Durable continuity must preserve every Daybreak frozen boundary, access-context ID, route disposition/evidence, blocker/reopen condition, preflight receipt, refusal provenance, custody state, and task-attempt state. No AMS-specific recovery file is created.

## 16. Completion and failure

Workers and managers return evidence claims; only the root accepts project completion. Ordinary failures use normal correction/rerouting. A closed Daybreak route survives recovery until its explicit reopen condition is met. An uncertain task start blocks another task attempt; every terminal outcome after confirmed start consumes the unit. Unobservable route identity is recorded as unavailable without a false attestation claim.

## 17. Update, repair, and uninstall

Package mutation requires direct user authority. After an authorized install/update, AMS performs no automatic re-audit or project pause. Standard uninstall removes only the skill directory; settings and profiles remain unless separately authorized for cleanup.

## 18. Directory structure

```text
Codex-Adaptive-Master-Subagent-Orchestration/
├── README.md
├── INSTALLATION.md
├── PRODUCT DOCUMENTATION.md
├── SOL-ULTRA-AMS-EXTREME-ORCHESTRATION-PROMPT.md
├── install-manifest.txt
├── install.ps1
├── install.sh
└── adaptive-master-subagent-orchestration/
    ├── SKILL.md
    ├── VERSION
    ├── agents/openai.yaml
    ├── assets/agent-profiles/        # 19 profiles
    └── references/                   # 11 runtime references
```
