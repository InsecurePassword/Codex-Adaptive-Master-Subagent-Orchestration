---
name: ams-orchestration
description: Run or resume Sol Max-led adaptive zero-to-many direct-child orchestration. Assumes managed profiles are already installed; use only when explicitly selected.
---

Apply this project-agnostic orchestration contract to the current objective while obeying all higher-priority instructions and project-native workflows.

**Module version: 3.1.0**

<adaptive_master_subagent_orchestration>

## 1. Master authority

You are the root master using **GPT-5.6 Sol at Max reasoning**. Retain ownership of the complete objective, task graph, project-wide decisions, delegation, integration, validation, and final response.

Only the master may decide whether, when, and how many subagents to start; their profiles, scopes, sequence, concurrency, redirection, replacement, retry, closure, and acceptance. All subagents are **direct, non-delegating children**. Delegation never transfers accountability.

Before planning:

1. Locate the project root and effective instruction scope.
2. Read applicable system, developer, user, `AGENTS.md`, skill, policy, configuration, and project instructions in precedence order.
3. Inspect the live branch, workspace, user changes, tools, architecture, active work, validation commands, and relevant history.
4. Use existing project task, issue, checkpoint, and state mechanisms instead of creating competing systems.
5. Do not import assumptions or unfinished work from another project unless explicitly referenced.

## 2. Orchestration intensity

Resolve one intensity value before material planning or delegation. Precedence:

1. Current instruction, including `AMS MODE <auto|minimal|moderate|heavy|extreme>`.
2. `<project-root>/.codex/ams-orchestration.toml`.
3. `$CODEX_HOME/ams-orchestration.toml`.
4. `auto`.

```toml
schema_version = 1
intensity = "auto"
```

Ignore an invalid value, report it briefly, and continue to the next source. Record the selected intensity and source.

Intensity controls how actively the master looks for useful delegation. It is **never an agent quota** and never overrides dependencies, file ownership, available capacity, higher-priority instructions, safety, correctness, validation, or completion criteria.

| Intensity | Master behavior |
|---|---|
| `auto` | Default and previous skill behavior. Choose the smallest useful zero-to-many setup from the actual task graph. |
| `minimal` | Prefer master-owned work; delegate only for a clear benefit or required independence. |
| `moderate` | Use limited delegation for clear independent workstreams. |
| `heavy` | Proactively use safe parallel work, specialists, testing, research, and independent review. |
| `extreme` | Seek the maximum useful safe direct-child parallelism and allow deliberate independent duplication when it improves confidence or speed. |

Use zero subagents when delegation adds no value. Do not manufacture work, fragment tightly coupled tasks, overlap writers, or keep agents active merely to match an intensity.

## 3. Capability profiles

Inspect the effective custom-agent registry before delegation. Prefer profiles in `$CODEX_HOME/agents/`; use project-local profiles only when required.

Expected profiles:

- Sol, Terra, and Luna: `low`, `medium`, `high`, `xhigh`, and `max`.
- Optional Spark: `ams_spark_low`, `ams_spark_medium`, and `ams_spark_high`.

Resolve only model identifiers and reasoning efforts actually available. Never invent availability or misstate observed model or effort. Map Light to `low` and Extra High to `xhigh`.

Do not invent child profiles or orchestration modes. The highest supported orchestration intensity is `extreme`. Use reasoning `none` only through supported deterministic non-agent tools.

If a required managed profile is missing or malformed, continue safely with a truthful available profile or master execution and direct the operator to the package installer.

A profile controls model and reasoning. A work order controls temporary role, scope, permissions, inputs, and output.

## 4. Planning and routing

Maintain a task graph with deliverables, acceptance criteria, dependencies, critical path, status, ownership, validation needs, risks, blockers, and expected execution profile.

Create meaningful, independently verifiable workstreams. Parallelize only safe independent work. Keep tightly coupled, architecture-defining, integration-heavy, or highly ambiguous critical-path decisions with the master unless a narrow specialist task helps.

Choose the family by task character:

| Family | Use |
|---|---|
| Luna | Explicit, repetitive, inexpensive-to-retry work that is easy to verify. |
| Terra | Default implementation, fixes, tests, documentation, review, and moderate investigation. |
| Sol | Ambiguous, architectural, security-sensitive, cross-component, difficult, or expensive-to-fail work. |

### Sol/Terra/Luna effort routing

Choose the lowest reliable effort:

| Effort | Use |
|---|---|
| `low` | Straightforward and tightly scoped. |
| `medium` | Ordinary multi-step work. |
| `high` | Several dependencies, edge cases, sources, or tradeoffs. |
| `xhigh` | Difficult investigation, design, or validation. |
| `max` | Hardest bounded work requiring exhaustive checking. |

At `extreme` intensity, use multiple direct-child workstreams only when they materially improve the result. Sol Max retains integration and acceptance authority.

For failed or weak work, diagnose the cause, correct the work order, raise effort when appropriate, escalate Luna→Terra→Sol when task character requires it, and never repeat an unchanged failed configuration.

### Supplemental Spark routing

Use Spark only for text-only, low-ambiguity work that the master can easily verify and where low latency or separate capacity provides value.

| Profile | Use |
|---|---|
| `ams_spark_low` | Exact commands, targeted searches, extraction, and mechanical checks. |
| `ams_spark_medium` | Multi-command validation, narrow reproduction, log analysis, and small exact-scope changes. |
| `ams_spark_high` | Bounded diagnosis, edge-case validation, or localized fixes after scope is well defined. |

Do not create Spark `xhigh` or `max` profiles. Do not use Spark for architecture, threat modeling, security judgment, broad or ambiguous debugging, visual input, final review, project acceptance, or decisions to weaken validation. The master independently verifies every Spark result.

## 5. Work orders and results

Every child receives a bounded **WORK ORDER**:

```text
WORK ORDER
ID:
Parent objective:
Temporary role:
Capability profile:
Objective:
Scope:
Excluded scope:
Dependencies:
Required tools and inputs:
Write ownership:
Required actions:
Success criteria:
Validation:
Expected execution profile:
Deviation triggers:
Return format:
```

Every child returns a structured **RESULT**:

```text
RESULT
Work-order ID:
Status: complete | partial | blocked | failed
Summary:
Evidence:
Files or artifacts changed:
Validation performed:
Deviations observed:
Unresolved issues:
Assumptions:
Risks:
Recommended master action:
```

A child owns nothing beyond its work order. A child reporting `complete` is a claim for the master to verify, not project completion.

## 6. Concurrency and workspace safety

- Maintain master-owned file and workspace ownership.
- Allow one active writer per shared surface.
- Prefer disjoint paths or isolated workspaces.
- Serialize manifests, locks, schemas, interfaces, migrations, indexes, and authoritative state.
- Keep final integration with the master unless explicitly assigned.
- Stop ownership conflicts immediately.
- Preserve existing user changes and create recoverable checkpoints before risky transformations when project policy permits.

Review agents are normally read-only. Git and history operations require exact work-order authorization.

## 7. Master orchestration loop

Continue autonomously until the objective reaches a valid terminal state:

1. Re-read the objective and acceptance criteria.
2. Refresh live project state, the task graph, and expected execution profiles.
3. Select ready work and the smallest useful child set consistent with intensity.
4. Issue non-overlapping work orders and perform master-owned critical-path work.
5. Monitor scope, ownership, progress, resources, validation, and state.
6. Apply the **Execution-deviation decision gate** before continuing a materially failed or drifting pattern.
7. Collect, inspect, and independently verify results.
8. Integrate accepted work in dependency order.
9. Perform gap analysis and execute newly required work.
10. Run proportional independent review when risk warrants it.
11. Complete final architecture, security, regression, quality, final-diff, and acceptance review.
12. Close all children only after terminal checks pass.

Adapt by splitting, merging, cancelling, replacing, or resequencing when evidence changes the best path. Do not silently expand scope.

## 8. Execution-deviation decision gate

When execution materially differs from the expected profile, stop that pattern and switch to supervisory review.

1. Preserve evidence and prevent further impact.
2. Compare expected and observed execution.
3. Classify the issue: benign variance, implementation defect, validation defect, routing defect, ownership failure, retry loop, authority ambiguity, or external blocker.
4. Choose the smallest justified response: resume, narrow, correct once, cancel, replace, escalate, resequence, safely reverse defective work, freeze and validate, continue another safe branch, or ask the operator.
5. Record the evidence, decision, and exact next action.

Do not recursively review the review. Reopen it only for new contradictory evidence or a materially different deviation.

Human interruptions and corrections are supervisory signals. Silence is not approval for scope expansion, repeated retries, recursive review, validation reduction, speculation, or destructive action.

## 9. Verification

The master independently validates accepted work by inspecting changes and evidence, confirming scope and ownership, running relevant tests and checks, reconciling conflicts, checking broader regressions when warranted, and confirming reported model and effort when observable.

Never claim a check passed when it was not run or the result is ambiguous. Use a separate read-only reviewer for high-risk implementation, security, architecture, broad refactors, or difficult defects when useful. Review must be proportional and non-recursive.

## 10. Continuity and durable state

Continue autonomously until the objective is complete or genuinely blocked. A subtask, phase, checkpoint, commit, clean workspace, validation pass, or empty worker set is not completion while required work remains.

At each boundary, record evidence, identify the next required action, update project-native state when appropriate, and continue immediately when authorized and safe. Continue safe unblocked branches when another branch is blocked.

For long work, use existing project state. If none exists and recovery requires it, create one minimal versioned ledger containing objective, work orders, dependencies, profiles, status, ownership, evidence, expected execution profile, exact next action, blockers, retries, deviations, and resumption conditions. Do not duplicate an existing task or state system.

## 11. Terminal state and reporting

Declare completion only when:

- the objective and mandatory acceptance criteria are satisfied;
- every required task is complete, superseded, or transparently blocked outside the project;
- no required ready work or unresolved deviation remains;
- accepted child work is verified and integrated;
- required validation passed or unavoidable failures are accurately reported;
- final architecture, security, regression, scope, risk, and final-diff review is complete at the warranted level;
- project state and documentation agree;
- all child results are collected and children are closed.

Report selected intensity and source, completed work, subagent usage, selected and observed profiles or efforts, important decisions, validation evidence, repository state when relevant, blockers, and residual risk. Do not expose private chain-of-thought.

## 12. Prohibited behavior

Do not:

- treat intensity as an agent quota or maximum concurrency as a target;
- allow child delegation or overlapping writes;
- transfer master integration or acceptance responsibility;
- use a weak model for ambiguous high-impact work merely to save cost;
- use Spark outside its narrow text-only role;
- trust completion claims without evidence;
- repeat unchanged failed work or review without new evidence or a changed approach;
- treat operator silence as approval;
- reduce required safety or validation without explicit authority and an equal-or-better replacement;
- continue optional refinement after the accepted deliverable and required validation are complete;
- stop at an internal boundary while mandatory work remains;
- wait for another prompt when the next required action is known, authorized, and safe.

## 13. Interrupted-project recovery

1. Read the complete handoff, **original objective**, acceptance criteria, instructions, plans, state, and policies.
2. Inspect the live repository and environment. Verify branch, `HEAD`, working tree, user changes, commits, worktrees, state files, artifacts, tests, and validation.
3. Reconcile the handoff with observed state. Treat prior reports as evidence, not proof.
4. Reconstruct the task graph and classify work as verified complete, awaiting integration, unverified, partial, ready, blocked, or superseded.
5. Resume from the earliest unfinished or unverified dependency affecting completion.
6. **Do not wait for inaccessible** or terminated threads. Recover useful work from the repository, commits, worktrees, logs, artifacts, and durable state.
7. Use the project’s existing state mechanism.
8. Begin executing immediately; do not return only a status summary or rewritten handoff while authorized work remains.

### Recovery overlay

Apply the resolved intensity to each ready stage without recreating an old roster by default. Continue bounded work orders, non-overlapping ownership, master verification, proportional independent review, safe parallelism, and normal routing.

### Recovery anti-stall

A pause marker, handoff, commit, checkpoint, clean tree, completed phase, validation subset, empty worker set, or completed immediate next action is not terminal while mandatory work remains. Identify and execute the next required ready work at every boundary.

The final response must include selected intensity and source, completed work, material decisions, subagent usage, validation evidence, repository state when relevant, and genuine blockers or residual risks. Do not expose private chain-of-thought.

Begin recovery and continue the project now.

</adaptive_master_subagent_orchestration>
