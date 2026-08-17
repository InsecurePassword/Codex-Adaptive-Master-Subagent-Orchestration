# Product Documentation

**Product:** Adaptive Master–Subagent Orchestration (AMS)  
**Release:** 3.10

## 1. Product boundary

AMS keeps a GPT-5.6 Sol Max root, or verified equivalent Sol alias at Max reasoning, in control of the objective, task graph, physical dispatch, logical hierarchy, model/effort selection, ownership, integration, acceptance, and user communication. Bounded non-root sessions perform project work. Workers never delegate; delegated managers may request root-mediated descendants but never physically spawn or expand authority.

Every dispatch uses an explicit AMS profile. Requested configuration is routing evidence, not independent attestation of effective runtime identity.

## 2. Installed components and side effects

The standard installer writes only:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
$CODEX_HOME/agents/ams_*.toml
```

It installs 19 profiles, does not edit `$CODEX_HOME/config.toml`, project settings, ACLs, or general permissions, and leaves profiles after standard uninstall. AMS may create `<project-root>/.codex/ams-orchestration.toml` only under `project-control.md`. It never creates an AMS recovery file.

## 3. Installation and trust

Canonical installers fetch `install-manifest.txt` and its exact 33-file set from repository `main`, verify byte lengths and SHA-256 values, reread the manifest for equality, stage the full package, and install transactionally with profile rollback. See [INSTALLATION.md](INSTALLATION.md).

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

Daybreak adds no setting, status field, availability cache, or schema migration. Unknown, duplicate, nested, invalid, or unsupported settings remain errors.

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
| Daybreak Blue | Refusal-triggered worker-only fallback for one unchanged authorized defensive cybersecurity task. |

Daybreak has only `max` because it is an access-path fallback, not a cost tier.

## 7. Daybreak Blue contract

### 7.1 Trigger and frozen task

Daybreak is never proactive. It is considered only after an explicit qualifying cyber-safeguard refusal during root handling or from a standard Sol `worker` or `delegated-manager`, when the still-required task is authorized defensive work and its target, scope, exclusions, authority, permissions, data handling, and operational effect remain unchanged.

Generic failure, weak output, timeout, missing context/tools, sandbox or approval denial, network restriction, quota/account failure, unsupported effort, or non-cyber refusal is not a trigger.

Assign one stable fallback-unit ID to the frozen task. Equivalent refusals, retries, replacement, replication, resumed work, and reparenting map to the same unit.

```text
Attempt state: not-started | active | consumed
```

### 7.2 Canonical access-route record

Route availability is owned by one root-level canonical record, not copied into every fallback unit. Its deterministic key includes:

```text
Provisioned access path and execution surface
Approved identity and organization/workspace/API-project boundary
Internal-only status
Retention requirement and coverage
Exact Daybreak profile SHA-256, model, and effort
Signed-in Codex session generation, platform-observed when available or root-generated for the current top-level session after explicit identity/path confirmation
```

Record:

```text
Route record ID / generation
Route disposition: unverified | verifying | verified | closed-unavailable
Reserved fallback unit ID
Verification operation ID / attempt
Route evidence / blocker / reopen condition
Verified unit / logical parent / custody / intensity binding
```

Every unit with the same key references the same record. One record permits one active verification/task reservation. Verification is unit-, parent-, custody-, intensity-, objective-, and session-bound and is not reusable across units. Dispatch the admitted task in the same uninterrupted orchestration wave; before confirmed task start, interruption, compaction, handoff, root replacement, approval wait, or identity/path uncertainty invalidates verification and requires a new generation.

After the admitted task terminates, clear the reservation and return to `unverified` unless authoritative evidence requires `closed-unavailable`. A closed record applies to all units sharing the key and survives replacement, reparenting, compaction, handoff, root replacement, and recovery. Only explicit new provisioning evidence or an explicit user-directed recheck after material context change creates a new generation.

Late results are accepted only when generation, operation ID, nonce, reserved unit, logical parent, and work-order ID match. They cannot overwrite a newer generation or reopen a closed route.

### 7.3 Provisioned access path and data boundary

Before verification, the root records:

```text
Provisioned access path: codex-workspace | api-organization | user-or-model-specific
Execution surface: codex-interactive | codex-security-plugin | codex-cli | codex-github-action | responses-api | approved-codex-api-workflow | exact-provisioned-surface
Approved identity or membership basis
Approved organization/workspace/project boundary
Internal-only use confirmed: yes
Retention requirement and coverage
Provisioning and retention evidence IDs
Signed-in session generation
Access-context fingerprint
```

Compatibility:

- `codex-workspace` uses only a Codex surface explicitly covered by the named internal Codex/ChatGPT organization or workspace.
- `api-organization` uses only the Responses API or an explicitly approved Codex API workflow authenticated to the named internal API organization/project.
- `user-or-model-specific` uses only the exact surface confirmed by OpenAI; `none-user-level` is valid only when confirmation explicitly states no organization/workspace/project applies.
- Workspace and API paths use separate route records.

A profile, installation, model catalog, prior session, or absence of an error is not access proof. Fail closed when path, surface, identity, boundary, internal-only status, session generation, or required retention coverage cannot be established. ZDR/custom retention must be confirmed for the exact boundary and surface.

### 7.4 Capability-verification preflight

The exact fallback unit must reserve the route record and verify capability before receiving project ownership or task data.

The verification session receives no project files, repository content, telemetry, malware samples, credentials, secrets, customer data, refusal evidence, target details, project/Git ownership, mutation authority, non-public collection authority, or live-target interaction. The approved OpenAI workflow may read only its exact public references through existing authorized network access.

Proof modes:

1. platform-attested effective Daybreak identity;
2. the current bounded defensive validation workflow supplied through OpenAI onboarding;
3. a public or organization-approved, non-project, local-only defensive fixture with explicit expected results, where the identical fixture first received a qualifying standard-Sol cyber-safeguard refusal in the current session.

Synthetic fixtures may use inert toy code/static artifacts for defensive analysis but may not contain user/customer data, a live target, credentials, working malware, persistence/stealth, an exploit chain, external side effects, or deployment instructions.

The verification work order records the route generation, reserved unit, operation ID/nonce, proof mode, fixture and expected result, standard-Sol control result where required, access context, logical parent/custody/intensity, requested route, and no-data/no-ownership constraints.

Every verification session returns universal `RESULT` plus `DAYBREAK CAPABILITY PREFLIGHT ADDENDUM`. The root validates result custody, route generation, operation ID, nonce, unit binding, proof evidence, expected result, role, and no-data/no-mutation claims. A nonce echo proves transport only and never verifies capability.

### 7.5 Verification budget

A route generation permits at most:

1. one initial Daybreak verification process-start attempt;
2. one retry only when the first failure is proven to have occurred before any Daybreak session started and was a temporary transport/capacity failure.

Any confirmed or uncertain start/result, malformed or non-distinguishing result, failed criterion, refusal, substitution, mismatch, entitlement/access failure, incompatible context, or second no-start failure closes the route. No automatic retry follows. A material provisioning change requires explicit evidence and a new route generation.

### 7.6 Lineage, intensity, and ownership

Daybreak sessions are physical root children with `worker/none` but preserve logical parentage.

- Root-origin refusal: parent `root`.
- Refused Sol worker: close/supersede it, prove it non-live, and preserve its parent.
- Refusing Sol manager in `balanced`, `heavy`, `extreme`, or Rush: manager remains parent, relinquishes the affected surface, and does not write concurrently.
- Refusing manager in `minimal`: manager records the request, relinquishes ownership, reaches a boundary, and closes as `inactive-resumable`; any required standard-Sol control, verification, and task run serially as the only active non-root session; the manager resumes or is superseded afterward.
- Unavailable parent/flattening: use existing hierarchy supersession and custody transfer.

Every control/verification/task session consumes one ordinary worker slot while active. One-writer safety and finite allocation remain mandatory.

### 7.7 Task attempt and completion

After verification, recheck route generation/binding, profile hash, access context, custody, ownership, and `Attempt state = not-started`; then transfer only minimized data needed for the unchanged task.

Task process start permits one initial start plus one retry only after a proven temporary no-start transport/capacity failure. A second no-start or authoritative route/context error closes the route while leaving the unit `not-started` and blocked. A confirmed start sets `active`; every terminal result after confirmed start sets `consumed`; an uncertain start remains `active` until closure is proved. AMS never repeats, fans out, rotates, or resets the task through replacement, reparenting, recovery, Extreme, or Rush. It never automatically escalates to Daybreak Red, GPT-5.6 Cyber, an offensive workflow, or root execution.

The task returns universal `RESULT` plus `DAYBREAK RESULT ADDENDUM`. Physical return to root is transport; evidence is reconciled through the logical parent or superseding custodian. Daybreak output is evidence, not project acceptance.

After terminal handling, release the canonical route reservation and return the record to `unverified` unless authoritative route/capability evidence requires closure.

## 8. Permission and data neutrality

No profile grants sandbox, approval, network, writable-root, tool, credential, target, or authorization privilege. Daybreak inherits existing platform/user/project/work-order controls.

Capability verification receives no project data. The task receives only its frozen objective, minimal relevant code/artifacts/telemetry, bounded refusal evidence, and authorization basis. AMS creates no Daybreak cache, transcript service, external uploader, or recovery ledger. Data remains subject to the exact approved surface's controls and retention terms; Trusted Access and ZDR/custom retention are separate provisioning decisions.

## 9. Profile installation and repair

Existing profiles are handled strictly:

- exact current bytes: unchanged;
- exact recognized prior official Spark bytes: upgraded during authorized install/update;
- missing profile: created;
- any other differing profile: preserved and blocks replacement.

Runtime auto-management may create a selected missing profile only. It cannot overwrite differing content or repair Daybreak by changing credentials, workspaces, API projects, surfaces, permissions, or retention controls.

## 10. Root authority, work orders, and hierarchy

Valid role/authority pairs are `worker/none` and `delegated-manager/request`. The root alone physically spawns, owns global routing/state, accepts results, declares completion, and communicates with the user. Every non-root order has one immutable logical parent.

All sessions may remain physical root children while work-order lineage records logical parentage. Authority, permissions, scope, ownership, and allocation may narrow but never expand. One active writer is allowed per mutable surface. Results pass through the logical parent before root acceptance.

## 11. Root execution boundary and fallback

The root is management and does not perform project inspection, research, implementation, commands, deployment, tests/builds/linting, security checks, independent review, Git/history operations, or artifact generation while a compliant delegated route exists.

Root fallback is a bounded, low-risk, reversible last-resort unblocker and is ineligible for security-sensitive execution. An unavailable or exhausted Daybreak route never authorizes the root to perform the refused cyber task.

## 12. Configuration maintenance

The explicit updater preserves existing supported values, adds only missing defaults, rejects invalid content, and never runs implicitly. A missing project file may inherit valid global values; `AMS CONFIGURATION UPDATE GLOBAL` may create only the exact disabled global default.

## 13. Intensity and Rush

`minimal`, `balanced`, `auto`, `heavy`, and `extreme` change team formation, not quality, safety, ownership, or completion authority. Rush requires explicit current-turn consent. Neither Extreme nor Rush makes Daybreak proactive, duplicates a unit, bypasses verification, reopens a closed route, or increases verification, task process-start, or confirmed-task budgets.

## 14. Optional project governance and continuity

When enabled, governance adds lifecycle tracking, proportional validation/review, deviation handling, and continuity through existing project-native state or a user-visible handoff. It does not change core authority or Daybreak gates.

Durable continuity preserves each fallback unit and each canonical route record, including key inputs, generation, disposition, reservation, bound unit/topology, profile hash/model/effort, signed-in session generation, verification evidence/budget, blocker, and reopen condition. No AMS-specific recovery file is created.

## 15. Completion and failure

Workers/managers return evidence claims; only root accepts project completion. Ordinary failures use normal correction/rerouting. Closed route state survives recovery until explicit reopen conditions are met. Unobservable route identity is reported as unavailable without false attestation.

## 16. Update, repair, and uninstall

Package mutation requires direct user authority. After authorized install/update AMS performs no automatic re-audit or project pause. Standard uninstall removes only the skill directory; settings/profiles remain unless separately authorized for cleanup.

## 17. Directory structure

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
