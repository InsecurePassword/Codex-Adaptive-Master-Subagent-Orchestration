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
| Daybreak Blue | Worker-only one-shot fallback for an unchanged authorized defensive cybersecurity work unit explicitly refused by standard Sol for cyber-safeguard reasons. |

Reasoning levels are `low`, `medium`, `high`, `xhigh`, and `max`; Spark supports only Low through High. Daybreak Blue exposes only the canonical Max profile because it is an access-path fallback, not a cost tier. The root selects the lowest-cost reliable normal route and records substitutions. File count alone does not justify a stronger model.

Every successful spawn is reported concisely with its requested profile. AMS never presents the requested profile as observed identity when the runtime cannot expose it.

### 6.1 Daybreak Blue fallback contract

Daybreak Blue is not selected proactively. The root loads `references/daybreak-blue.md` only after it receives an explicit cyber-safeguard refusal during root handling or from a standard Sol worker for a still-required task and all of these conditions are satisfied:

- the user owns, operates, or is explicitly authorized to test or analyze the relevant system, application, account, network, code, artifact, or data;
- the purpose is authorized defensive security, including Secure SDLC/AppSec, secure review/patching, threat modeling, threat intelligence, threat hunting, malware analysis, detection engineering, vulnerability triage/validation, incident response, or patch validation;
- the objective, target, scope, exclusions, permissions, authority, and operational boundary remain frozen;
- no independent higher-priority safety, authorization, ownership, or project control blocks the work.

Generic errors, timeouts, weak or partial answers, missing tools/files/context, sandbox or approval denials, account/quota failures, and non-cyber refusals are not triggers. The Daybreak work order records the original Sol route, bounded refusal evidence, authorization basis, frozen scope, and `1 of 1` attempt budget. Daybreak is always `worker`/`none`, cannot delegate, and cannot broaden or operationalize the task beyond the refused defensive objective.

A started Daybreak refusal/failure consumes the attempt. AMS does not repeat the unchanged setup, split the same refusal across multiple Daybreak workers, alter credentials or permissions, or escalate automatically to Daybreak Red, a cyber-specialized model, an offensive workflow, or root execution. Output remains evidence requiring root reconciliation and normal independent validation where required and safely possible.

The profile requests `gpt-daybreak-blue-latest`; installation proves only the configured route. Account, workspace, product-surface, or entitlement unavailability is reported as an exact blocker. Daybreak access never establishes authorization or relaxes platform/user/project/work-order boundaries.

## 7. Permission neutrality

Profiles select model/access lane and reasoning only; they do not grant permissions. No current profile contains `sandbox_mode`, approval-policy, network, writable-root, authorization, or tool-grant overrides. Spark and Daybreak Blue inherit the same platform/user/project/work-order permission policy as Sol, Terra, and Luna.

Every profile still embeds the minimal orchestration constraints required for coordinated operation: explicit work order, root-only physical spawning, worker leaf behavior, manager request-only delegation, root-only user communication, and root-only completion authority. The Daybreak profile additionally requires its qualifying-refusal and frozen-scope fields.

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

## 10. Virtual hierarchy and ownership

All physical sessions may remain root children while work-order lineage records logical managers and workers. The root validates every manager dispatch request, assigns the child work-order ID, records ownership/allocation, and performs the spawn.

One active writer is allowed per mutable surface. Authority, scope, ownership, permissions, and allocation may narrow but never expand down the tree. Only the root accepts project completion.

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

Zergling Rush is separate and requires explicit current-turn consent. It may use stronger routes, competing approaches, speculative preparation, duplicate investigation, and redundant validation, but never changes root authority, permissions, ownership, safety, or completion rules. It does not make Daybreak Blue proactive or increase its one-attempt budget.

## 15. Optional project governance

`project_governance = true` loads `references/project-governance.md`. It adds:

- explicit project-wide acceptance and dependency tracking;
- proportional executable validation and independent review;
- continuation while a known authorized action remains;
- deviation classification and correction;
- continuity through an existing project-native system or user-visible handoff.

`AMS GOVERNANCE off` disables only those AMS-added requirements. Core orchestration, hierarchy, ownership, model/effort routing, work orders, safety, and truthful completion remain active.

AMS does not create an independent recovery ledger. The live root task graph manages active workers; durable continuity uses already-authorized project-native state or a concise handoff.

## 16. Completion and failure

Worker and manager completion are evidence claims. The root reconciles results and declares completion only when the user/project-defined objective and checks are satisfied, no mandatory work or conflicting writer remains, and any enabled governance requirements are met.

On ordinary failure, the root corrects work orders, reroutes, raises effort, escalates family, replaces sessions, changes topology, or reports a genuine blocker. It never repeats an unchanged failed setup or invents observed identity. A qualifying standard-Sol cyber refusal follows the separate bounded Daybreak contract.

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
