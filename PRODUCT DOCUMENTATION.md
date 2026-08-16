# Product Documentation

**Product:** Adaptive Master–Subagent Orchestration (AMS)  
**Release:** 3.10

## 1. Product boundary

AMS has two core responsibilities:

1. keep a GPT-5.6 Sol Max root, or verified equivalent Sol alias at Max reasoning, in control of subagent selection, physical dispatch, logical hierarchy, sequencing, ownership, integration decisions, acceptance, and user communication;
2. select and request the model family, access lane, and reasoning effort for every bounded non-root session through an explicit AMS profile.

The root is a management lane. It delegates project execution whenever a compliant bounded route exists. Workers are leaves. Delegated managers may request root-mediated descendants but never physically spawn or expand authority.

AMS reports the requested profile after each successful spawn. Requested configuration is best-effort routing evidence, not independently attested runtime identity.

## 2. Installed components and side effects

The standard installer writes:

```text
$HOME/.agents/skills/adaptive-master-subagent-orchestration/
$CODEX_HOME/agents/ams_*.toml
```

It installs 19 global profiles and leaves them after standard uninstall. It does not edit `$CODEX_HOME/config.toml`, project settings, operating-system ACLs, or other Codex configuration.

AMS runtime may create the project settings file when neither project nor global AMS settings exist:

```text
<project-root>/.codex/ams-orchestration.toml
```

It never creates `.codex/ams-recovery.json` or another AMS-specific recovery file.

## 3. Installation and trust

The canonical installers read `install-manifest.txt` and each declared file directly from the repository `main` tree. They expose no source/ref/manifest environment override. A noncanonical source requires a separate explicit manual procedure.

Every file is length- and SHA-256-verified, and the manifest must be identical before and after download. The complete skill is staged and installed transactionally with profile rollback.

See [INSTALLATION.md](INSTALLATION.md) for commands and verification.

## 4. Settings and precedence

Project settings:

```text
<project-root>/.codex/ams-orchestration.toml
```

Global settings:

```text
$CODEX_HOME/ams-orchestration.toml
```

When `CODEX_HOME` is unset, use `$HOME/.codex/ams-orchestration.toml`.

A project file is a complete override. Global settings apply only when no project file exists. The files are not merged. A project-setting command creates an absent project file from valid effective global values when available, otherwise from the exact default, then changes only the requested key.

Schema 2 is the only supported schema:

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

Daybreak Blue adds no setting, status field, availability cache, or schema migration. The lane is evaluated only after a qualifying refusal.

Any omitted currently supported schema-2 setting resolves from the exact current default and is persisted during the next authorized settings write. Unknown, duplicate, nested, invalid, or unsupported content remains an error.

| Setting | Meaning |
|---|---|
| `enabled` | Persistent AMS activation for this settings source. |
| `allow_implicit_invocation` | Allows automatic skill activation when Codex permits it. |
| `intensity` | Team-formation posture: `auto`, `minimal`, `moderate`/`balanced`, `heavy`, `extreme`, or stored Rush preference. |
| `project_governance` | Default-on optional project lifecycle, review, acceptance, and continuity layer. |
| `root_execution_fallback` | Default-on bounded last-resort root action for standard AMS when no viable delegated route remains. |
| `spark_enabled` | User preference for normal Spark routing. |
| `spark_available` | Cached Spark availability evidence. |
| `spark_efforts` | Allowed normal Spark efforts. |
| `profile_management` | Missing-profile behavior: `auto` or `installer`. |

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

Normal persistent controls write only the project file. `AMS STATUS` is read-only. `AMS MODE` also enables AMS. `AMS GOVERNANCE` changes only the optional governance layer. `AMS CONFIGURATION UPDATE GLOBAL` is the sole explicit global-writing command and only adds missing defaults or creates the exact disabled default.

## 6. Model and reasoning control

Supported profiles:

```text
ams_<sol|terra|luna>_<low|medium|high|xhigh|max>
ams_spark_<low|medium|high>
ams_daybreak_blue_max
```

| Family or lane | Intended work |
|---|---|
| Spark | Bounded mechanics with little judgment; worker-only. |
| Luna | Explicit repetitive low-risk work. |
| Terra | Normal implementation, tests, documentation, review, and investigation. |
| Sol | Ambiguous, architectural, security-sensitive, difficult, or expensive-to-fail work. |
| Daybreak Blue | Root-spawned worker-only one-attempt fallback for an unchanged authorized defensive cybersecurity work unit explicitly refused by standard Sol for cyber-safeguard reasons. |

Reasoning levels are `low`, `medium`, `high`, `xhigh`, and `max`; Spark supports only Low through High. Daybreak Blue exposes only the canonical Max profile because it is an access-path fallback, not a cost tier. The root selects the lowest-cost reliable normal route and records substitutions. File count alone does not justify a stronger model.

Every successful spawn is reported concisely with its requested profile. AMS never presents the requested profile as observed identity when the runtime cannot expose it.

### 6.1 Daybreak Blue fallback contract

Daybreak Blue is not selected proactively. The root loads `references/daybreak-blue.md` only after it receives an explicit cyber-safeguard refusal during root handling or from a standard Sol non-root execution order for a still-required task and all of these conditions are satisfied:

- the user owns, operates, or is explicitly authorized to test or analyze the relevant system, application, account, network, code, artifact, or data;
- the purpose is authorized defensive security, including Secure SDLC/AppSec, secure review/patching, threat modeling, threat intelligence, threat hunting, malware analysis, detection engineering, vulnerability triage/validation, incident response, or patch validation;
- the objective, target, scope, exclusions, permissions, authority, and operational boundary remain frozen;
- no independent higher-priority safety, authorization, ownership, or project control blocks the work.

Generic errors, timeouts, weak or partial answers, missing tools/files/context, sandbox or approval denials, account/quota failures, and non-cyber refusals are not triggers.

Before first dispatch, the root assigns a stable Daybreak fallback unit ID bound to the frozen task. Equivalent refusals from duplicated, replacement, resumed, or reparented Sol orders map to the same unit. Its attempt state is `not-started`, `active`, or `consumed`, and the state must be preserved in existing project-native continuity or a user-visible handoff when durable continuity is required. No new AMS recovery file is created.

Refusal provenance is explicit:

```text
Refusal source: root-handling | work-order
Original Sol work-order ID: none-root-handling | <stable work-order ID>
Original Sol role: root | worker | delegated-manager
Original logical parent: root | <work-order ID>
Refusal evidence ID: <stable root-recorded identifier>
```

A root-origin refusal uses the exact `none-root-handling` sentinel. A refusal from a standard Sol delegated manager is eligible when the manager performed bounded execution.

The Daybreak worker is physically spawned by the root and is always `worker`/`none`, but physical root dispatch does not force logical parent `root`. A refused Sol worker is closed or superseded before Daybreak receives the same logical parent and transferred ownership. A refusing delegated manager remains the logical parent, relinquishes execution ownership of the affected surface, and supervises the Daybreak descendant. If the parent is unavailable or the chain is deliberately flattened, AMS uses the existing explicit supersession and custody-transfer rules. The worker consumes a normal worker slot and allocation and may not violate the selected intensity shape.

A confirmed successful start changes the unit to `active`; every terminal outcome after a confirmed start changes it to `consumed`. AMS does not repeat, replicate, rotate, reparent-reset, or automatically escalate the unit to Daybreak Red, another cyber-specialized model, an offensive workflow, or root execution. Extreme and Zergling Rush do not increase the budget.

### 6.2 Daybreak route evidence and access

The profile requests:

```text
profile=ams_daybreak_blue_max
model=gpt-daybreak-blue-latest
effort=max
```

Exact profile bytes establish requested configuration only. A successful spawn with no explicit model mismatch, entitlement error, approved-workspace/product-surface error, or access-path error is sufficient requested-route evidence to begin work; it is not model attestation. Record observed identity when exposed. Otherwise record `observed=unavailable` and do not require worker self-attestation.

An explicit mismatch or access error blocks the route. AMS does not change credentials, organizations, workspaces, permissions, or product surfaces automatically. Access must already be provisioned to the exact approved internal Codex organization/workspace and product surface.

The Daybreak work order and terminal addendum record the stable unit, attempt state, refusal provenance, original and final logical parent, custody, prior-writer closure, ownership transfer, allocation, frozen boundary, requested route, observed route, and residual blockers.

## 7. Permission and data neutrality

Profiles select model/access lane and reasoning only; they do not grant permissions. No current profile contains `sandbox_mode`, approval-policy, network, writable-root, authorization, or tool-grant overrides. Spark and Daybreak Blue inherit the same platform/user/project/work-order permission policy as Sol, Terra, and Luna.

Every profile embeds the minimal orchestration constraints required for coordinated operation: explicit work order, root-only physical spawning, worker leaf behavior, manager request-only delegation, root-only user communication, and root-only completion authority. The Daybreak profile additionally requires its fallback-unit, provenance, custody, frozen-scope, route-evidence, and one-attempt fields.

Daybreak work orders use data minimization. They include only the bounded objective, relevant evidence, authorization basis, required code/artifacts/telemetry, and a small redacted refusal excerpt or summary. They do not automatically forward unrelated conversation history, files, credentials, secrets, or entire repositories.

AMS creates no Daybreak-specific cache, recovery file, transcript store, or external upload service. Data submitted through the approved Daybreak surface remains subject to that OpenAI organization/workspace's data controls and retention terms. Trusted Access and Zero Data Retention are separate provisioning decisions.

## 8. Profile installation and repair

The installer deploys all 19 profiles. Existing profile handling is strict:

- exact current bytes: unchanged;
- exact prior official Spark bytes with the former `workspace-write` field: upgraded during a direct user-authorized install/update;
- missing profile: created;
- every other differing profile: preserved and blocks replacement.

A managed marker alone never authorizes overwrite. Runtime `profile_management = "auto"` may create a selected missing profile only; it does not replace an existing differing file. Explicit repair uses the same provenance rules.

## 9. Root authority and work orders

The root owns the objective, task graph, physical dispatch, model/effort routing, logical topology, sequencing, ownership, retries, integration decisions, acceptance, completion, and user communication.

Every non-root session receives a stable work order with objective, scope, exclusions, dependencies, role/authority, capability profile, permissions, ownership, validation, and return requirements. Valid pairs are:

```text
worker / none
delegated-manager / request
```

Workers never delegate. Managers request descendants through the root. Spark and Daybreak Blue are always workers. Every order has one immutable logical parent.

A Daybreak work order is a new stable work-order ID associated with a separately stable fallback unit ID. Replacing or reparenting a normal Sol order does not reset the fallback unit or its consumed state.

## 10. Virtual hierarchy and ownership

All physical sessions may remain root children while work-order lineage records logical managers and workers. The root validates every manager dispatch request, assigns the child work-order ID, records ownership/allocation, and performs the spawn.

One active writer is allowed per mutable surface. Authority, scope, ownership, permissions, and allocation may narrow but never expand down the tree. Only the root accepts project completion.

Daybreak preserves the refused work's logical parent by default. A refused worker must be closed or superseded and proven non-live before ownership transfer. A delegated manager that produced the refusal becomes the Daybreak worker's logical parent and may not write the same surface concurrently. Result transport through the root does not bypass logical-parent reconciliation.

## 11. Root execution boundary

The root does not perform project inspection, research, implementation, commands, deployment, tests/builds/linting, security checks, independent review, integration execution, Git/history operations, or artifact generation while a compliant delegated route exists. The root changes routing and supervision rather than taking over cheaper-model work.

## 12. Root execution fallback

Standard AMS defaults to `root_execution_fallback = true`, but the root remains a management lane while a viable lower-cost delegated route exists. Only a genuine no-viable-route blocker loads the fallback reference. One bounded atomic action is allowed per blocker episode, ownership must be reclaimed before mutation, root-visible output is bounded, and a mutation remains pending independent validation. An exhausted Daybreak attempt does not authorize the root to execute the refused cybersecurity task. Zergling Rush and the separate Sol Ultra prompt retain their own mode-specific root rules.

## 13. Configuration maintenance

The explicit updater supports both existing and missing files:

- existing project or global file: preserve every existing supported value and add every missing current field from the exact default;
- missing project file: use valid global settings when present, use the exact default when the global file is absent, and reject without writing when an existing global file is invalid or unsafe;
- missing global file: `AMS CONFIGURATION UPDATE GLOBAL` may create the exact disabled default;
- complete file: validate and perform no write;
- unknown, duplicate, nested, invalid, or unsupported content: reject without writing.

The updater is never loaded implicitly.

## 14. Intensity and Rush

- `minimal`: root plus at most one active non-root session;
- `balanced`/stored `moderate`: one bounded small-team shape;
- `auto`: smallest useful adaptive topology;
- `heavy`: proactive useful managers and parallel lanes;
- `extreme`: every useful ready safe lane, still cost-first.

Zergling Rush is separate and requires explicit current-turn consent. It may use stronger routes, competing approaches, speculative preparation, duplicate investigation, and redundant validation, but never changes root authority, permissions, ownership, safety, or completion rules. It does not make Daybreak Blue proactive, duplicate a stable fallback unit, or increase its one-attempt budget.

## 15. Optional project governance

`project_governance = true` loads `references/project-governance.md`. It adds:

- explicit project-wide acceptance and dependency tracking;
- proportional executable validation and independent review;
- continuation while a known authorized action remains;
- deviation classification and correction;
- continuity through an existing project-native system or user-visible handoff.

`AMS GOVERNANCE off` disables only those AMS-added requirements. Core orchestration, hierarchy, ownership, model/effort routing, work orders, safety, and truthful completion remain active.

AMS does not create an independent recovery ledger. The live root task graph manages active workers and Daybreak attempt state; durable continuity uses already-authorized project-native state or a concise handoff.

## 16. Completion and failure

Worker and manager completion are evidence claims. The root reconciles results and declares completion only when the user/project-defined objective and checks are satisfied, no mandatory work or conflicting writer remains, and any enabled governance requirements are met.

On ordinary failure, the root corrects work orders, reroutes, raises effort, escalates family, replaces sessions, changes topology, or reports a genuine blocker. It never repeats an unchanged failed setup or invents observed identity. A qualifying standard-Sol cyber refusal follows the separate bounded Daybreak contract.

For Daybreak, uncertainty about whether a worker started blocks a second attempt until closure is proven. Every terminal outcome after confirmed start consumes the stable unit. Route identity may remain unobservable without invalidating the result, but no observation claim may be made.

## 17. Update, repair, and uninstall

Package mutation requires direct user authority. Installer manifest, hash, provenance, and transaction checks occur only inside the requested mutation. After completion, AMS performs no package comparison, re-verification, re-audit, reactivation, project suspension, or user-action gate unless package-integrity verification is directly requested. The standard installer uses only canonical `main`, validates the exact 33-file set, and never edits general Codex configuration or permissions.

Standard uninstall removes only the skill directory. Project/global settings and installed profiles remain for troubleshooting or reinstall. Separate profile cleanup requires explicit authorization and proven AMS ownership.

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
    ├── assets/agent-profiles/        # 19 profiles, including ams_daybreak_blue_max
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
