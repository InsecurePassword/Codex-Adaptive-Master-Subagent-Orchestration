# Adaptive Master–Subagent Orchestration

**Current release: 3.10**

Adaptive Master–Subagent Orchestration (AMS) is a Codex skill that keeps **GPT-5.6 Sol Max** in charge while routing bounded project work to the lowest-cost reliable subagent model and reasoning effort.

The two core functions are:

1. **Sol Max controls orchestration.** The root owns the objective, task graph, physical spawning, logical hierarchy, routing, integration decisions, acceptance, and user communication. Workers are bounded leaves; delegated managers may request root-mediated descendants.
2. **AMS controls requested model and reasoning effort.** Every non-root dispatch uses an explicit AMS profile. AMS reports the requested profile after spawn without claiming that the runtime identity was independently observable.

Profiles do not grant sandbox, approval, network, writable-root, tool, authorization, or other permission overrides. Spark and the optional Daybreak Blue fallback inherit the same platform/user/project/work-order boundaries as every other route.

## Install

The installers fetch each required file directly from the canonical `main` repository tree through `install-manifest.txt`. They do not use GitHub Release assets or a package ZIP.

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

When `CODEX_HOME` is unset, profiles use `$HOME/.codex/agents/`. The installer does **not** edit `$CODEX_HOME/config.toml`, project settings, or operating-system permissions.

For a complete source copy:

```bash
git clone https://github.com/InsecurePassword/Codex-Adaptive-Master-Subagent-Orchestration.git
```

See [INSTALLATION.md](INSTALLATION.md) for exact validation, profile-collision, update, repair, and uninstall behavior.

## Persistence and settings

AMS checks project settings first, then global settings only when the project file is absent:

```text
<project-root>/.codex/ams-orchestration.toml
$CODEX_HOME/ams-orchestration.toml
```

Global configuration is never written implicitly. Normal project controls write only the current project file; `AMS CONFIGURATION UPDATE GLOBAL` is the sole explicit global-writing command and only adds missing defaults or creates the exact disabled default. If a project control creates a project file while valid global settings are active, AMS copies the resolved global values first and changes only the requested project setting.

Schema 2 default:

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

Daybreak Blue adds no setting and requires no schema migration. It remains dormant unless a qualifying refusal occurs.

Any omitted currently supported schema-2 setting resolves from the exact current default and is persisted during the next authorized settings write. Unknown, duplicate, nested, invalid, or unsupported content remains an error.

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

`project_governance = true` is the default. It adds AMS project-wide acceptance tracking, proportional independent review, continuous-delivery posture, deviation handling, and continuity through existing project-native state or a user-visible handoff.

Disable it for one project with:

```text
AMS GOVERNANCE off
```

Disabling governance does not change Sol-root control, model/reasoning routing, work orders, virtual hierarchy, root-only physical spawning, one-writer safety, or truthful completion.

## Model and effort routing

| Family or lane | Typical work |
|---|---|
| **Spark** | Exact commands, searches, extraction, routine tests/builds, formatting, and bounded mechanics. Worker-only. |
| **Luna** | Clear, repetitive, low-risk work that is easy to verify. |
| **Terra** | Normal implementation, fixes, tests, documentation, review, and moderate investigation. |
| **Sol** | Architecture, security-sensitive work, ambiguity, difficult debugging, and expensive-to-fail decisions. |
| **Daybreak Blue** | Worker-only, one-shot fallback for an unchanged authorized defensive cybersecurity work unit explicitly refused by standard Sol for cyber-safeguard reasons. Never normal routing. |

Sol, Terra, and Luna support `low`, `medium`, `high`, `xhigh`, and `max`; Spark supports `low`, `medium`, and `high`. Daybreak Blue has one canonical `max` profile: `ams_daybreak_blue_max`.

After a successful spawn AMS reports, for example:

```text
semantic_reviewer started: ams_sol_xhigh
```

That is the requested profile, not proof of observed runtime identity.

## Daybreak Blue

Daybreak Blue is an optional, refusal-triggered AMS worker lane for approved defensive cybersecurity work through OpenAI Daybreak and Trusted Access for Cyber. It is not a normal routing tier, a general-purpose stronger version of Sol, an offensive escalation path, or a persistent AMS setting. Installing AMS only installs the routing profile; it does not request, provision, or prove Daybreak access.

### When AMS activates it

AMS first uses normal cost-appropriate routing, with security-sensitive work ordinarily assigned to standard Sol. The root may dispatch `ams_daybreak_blue_max` only when all of the following are true:

- the task is lawful, authorized defensive cybersecurity work on a system, application, account, network, codebase, artifact, or data the user owns, operates, or is explicitly authorized to test or analyze;
- the Sol root received an explicit refusal attributable to cyber safeguards, either during root handling or from a standard Sol worker, for a bounded task that is still required;
- the objective, target, scope, exclusions, permissions, authorization, and operational boundary can remain materially unchanged;
- no higher-priority safety rule, authorization boundary, ownership conflict, or project-native control independently prohibits the work.

A weak, cautious, partial, or incorrect answer is not a qualifying refusal. Neither is a timeout, missing file or context, unavailable tool, sandbox or approval denial, network restriction, profile defect, account or quota error, unsupported effort, generic failure, or refusal unrelated to cybersecurity safeguards.

A qualifying work unit receives one direct Daybreak worker with a `1 of 1` attempt budget. Its work order includes the original Sol route, bounded refusal evidence, the authorization basis, and the frozen scope. The worker cannot delegate, become a manager, broaden the task, alter permissions, or contact the user. A started refusal, failure, or unusable result consumes the attempt; AMS does not repeat the unchanged request, fan it out to multiple Daybreak workers, rotate access profiles, or automatically escalate to Daybreak Red, another cyber-specialized model, an offensive workflow, or root execution.

### How AMS handles data

AMS applies data minimization to the fallback. The Daybreak work order carries only the information needed to complete the frozen task: the bounded objective and scope, a small exact excerpt or faithful redacted summary of the Sol refusal, the authorization basis, and the relevant code, artifacts, telemetry, or evidence required by that work unit. AMS does not forward unrelated conversation history, files, credentials, secrets, or the entire repository merely because the access lane changed.

The Daybreak worker inherits the same sandbox, approval, network, tool, writable-root, ownership, and Git-authority boundaries as the refused Sol route. It may inspect only the data required by the work order and reachable through those inherited controls. Daybreak access does not grant broader local access, additional network reach, new credentials, or authority to collect data from another target.

AMS does not create a Daybreak-specific cache, recovery file, transcript store, or external upload service. The worker returns its result to the Sol root for reconciliation. Any later independent validator receives only the evidence needed for its distinct validation work under normal AMS routing; Daybreak material is not automatically distributed to parallel workers.

Data submitted through Daybreak remains subject to the data controls and retention terms of the approved OpenAI organization or workspace and the product surface being used. **Trusted Access for Cyber does not include Zero Data Retention by default.** Zero Data Retention or other retention requirements must be arranged separately where available. Sensitive workflows should use the approved internal security workspace and should exclude unnecessary secrets, customer data, and unrelated production data.

### Trusted Access required

To use Daybreak Blue through AMS, the current Codex account must already have approved **Daybreak Blue / Trusted Access for Cyber** access on the organization or workspace and product surface where AMS is running. Approval is reviewed by OpenAI and is not automatic. The AMS profile cannot apply for access, transfer entitlement between workspaces, bypass provisioning, or make an unavailable model usable.

The approved organization or workspace should be reserved for approved internal security users and internal security workflows. Trusted Access must not be resold, proxied, embedded for third-party customers, exposed to external users, or used to power customer-facing applications or downstream product traffic. Work must remain within the approved defensive scope and within systems or data the user owns, operates, or is explicitly authorized to test or analyze.

Trusted Access provides more precise safeguards for verified defensive work; it does not remove all safeguards or refusals, authorize activity by itself, guarantee access to every cyber-specialized model, or include Daybreak Red. If Codex is not using the approved organization, workspace, model/access path, or product surface, AMS reports the exact access blocker and does not repeatedly probe or weaken the route.

See [OpenAI Daybreak — Trusted Access for Cyber Overview](https://help.openai.com/en/articles/20001258-openai-daybreak-trusted-access-for-cyber-overview) for current eligibility, workspace, authorization, retention, and usage requirements.

## Virtual hierarchy and root boundary

- The root is the sole physical spawn authority.
- Workers never delegate.
- Delegated managers request descendants through the root and remain bounded to their work orders.
- Spark and Daybreak Blue are always workers.
- Every non-root session has an immutable logical parent.
- One active writer is allowed per mutable surface.
- Only the root accepts project completion and communicates with the user.
- The root remains a management lane and does not take over project execution while a compliant delegated route exists.

## Root execution fallback

`root_execution_fallback = true` is the default for standard AMS operation. The root still delegates every task that a viable lower-cost session can complete and validate. The lazy fallback reference is loaded only when mandatory progress would otherwise stop and no viable delegated route remains. It permits one bounded low-risk atomic unblocker, protects ownership and root context, prevents chaining into a root implementation lane, and requires non-root validation before a root mutation can be finally accepted.

Disable it per project with:

```text
AMS ROOT FALLBACK off
```

Daybreak Blue is separate from root fallback: a qualifying cyber refusal is handled by a bounded non-root worker, and an exhausted Daybreak attempt does not authorize root execution of the refused cyber task. Specialized modes such as Zergling Rush and the separate Sol Ultra prompt retain their own stricter contracts.

## Configuration maintenance

```text
AMS CONFIGURATION UPDATE
AMS CONFIGURATION UPDATE PROJECT
AMS CONFIGURATION UPDATE GLOBAL
```

The project forms update an existing project schema-2 file by adding every currently supported missing field from the exact default while preserving every existing value. For a missing project file, valid global settings are used when present; an existing invalid or unsafe global file blocks the operation rather than being ignored. The explicit `GLOBAL` form performs the same missing-field update on the global file or creates the exact disabled default. No form changes an existing value or enables AMS.

## Intensity modes

| Mode | Posture |
|---|---|
| `minimal` | Root plus at most one active non-root session. |
| `balanced` | One small bounded direct-worker or manager team shape. |
| `auto` | Smallest useful adaptive topology. |
| `heavy` | Proactively forms useful managers and parallel lanes. |
| `extreme` | Dispatches every useful ready safe lane while remaining cost-first. |

`moderate` remains the schema-2 storage/command alias for `balanced`.

## Zergling Rush

Zergling Rush is a separate explicit-consent mode that may use stronger models, duplicate investigation, speculative preparation, and redundant validation to reduce wall-clock time. It never changes root authority, permissions, ownership, safety, or completion rules.

## Profile and installer safety

The installer deploys all 19 global profiles. A byte-identical profile is left unchanged. An exact prior official Spark profile may be upgraded to remove its former sandbox override. Any other differing, customized, marker-only, malformed, or user-authored profile is preserved and blocks replacement until the user reviews and reconciles it.

Installer transfer and transaction checks run only inside the explicitly invoked installer. After completion, AMS performs no package comparison, re-verification, re-audit, reactivation, project pause, or user-action gate unless the user directly requests package-integrity verification.

Standard uninstall removes only the skill directory and deliberately leaves settings and installed profiles for troubleshooting or reinstall.

## Requirements

- Codex with skills and custom-subagent support
- a top-level GPT-5.6 Sol Max session, or verified equivalent Sol alias at Max reasoning
- approved Daybreak Blue access on the active internal-security organization/workspace and Codex product surface when the optional fallback is needed
- Windows PowerShell 5.1+ for the PowerShell installer
- Bash plus `curl`, `awk`, `sort`, `cmp`, `mktemp`, `wc`, `tr`, `grep`, `head`, `tail`, `od`, `find`, `dirname`, and either `sha256sum` or `shasum`
