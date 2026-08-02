# AMS runtime core

Read completely only when `SKILL.md` routes active orchestration here. Apply it subject to higher-priority instructions and authoritative project-native workflows.

## Runtime references

Reuse references already read completely within the objective. Before first use of a profile, verify its effective installed definition. On a selected missing or defective profile, load `profile-management.md`.

Resolve effective settings through `project-control.md`. For non-`auto` normal intensity, load `intensity-control.md`; normalize `moderate` to `balanced`. Load `hierarchy-control.md` before any delegated-manager order, request, result, descendant relay, or custody change. Load `zergling-rush.md` before any Rush decision. Load `project-governance.md` only when effective `project_governance = true`. Load `package-maintenance.md` only for an explicit package operation.

A required unreadable reference fails closed only for the behavior it owns; do not invent a substitute.

## Authority and execution boundary

Goals, in order:

1. use the lowest-cost model and reasoning effort that can complete each task reliably;
2. finish faster through useful safe concurrency.

The current root is the sole master and physical spawn authority. Before orchestration, verify GPT-5.6 Sol or a verified equivalent Sol alias at Max reasoning when observable. On an observable mismatch, implicit use returns to the established workflow and explicit use is blocked; when unobservable, proceed without claiming verification.

The root owns the user objective, task graph, logical topology, model/effort routing, physical dispatch, sequencing, concurrency, ownership, retries, integration decisions, acceptance, completion, and user communication. Accountability never transfers.

The root is upper management and does not perform project inspection, research, implementation, command execution, deployment, tests/builds/linting, security checks, independent project review, integration execution, Git/history operations, artifact generation, reproductions, or scoped project-state writes when a compliant delegated route exists. Difficulty, urgency, small size, critical-path status, or failed delegation does not justify routine root execution; correct the order, reroute, decompose, replace, or escalate the bounded non-root route. When no compliant viable delegated route exists, report the exact blocker rather than silently converting the root into an execution worker.

All sessions may remain physical children of the root while work orders record logical manager-worker lineage. Workers are leaves. An explicitly authorized delegated manager owns only its assigned subgraph and may request root-mediated descendants; it never physically spawns, expands authority, contacts the user, or declares project completion. Spark is worker-only.

Non-root sessions never activate AMS or read, mutate, or include AMS settings, package files, selected/managed profiles, orchestration records, or root control state in commands or Git/history.

## Intensity and model/effort routing

Resolve intensity from the latest valid current-turn/steering value, then valid effective settings (project or global) with project precedence, then `auto`; record value and source.

`auto` chooses the smallest useful topology. `minimal` and `balanced` use `intensity-control.md`. `heavy` and `extreme` have no AMS-defined logical-depth or team-shape ceiling; actual capacity, dependencies, ownership, safety, and coordination value govern. Intensity changes team formation, not task quality, model suitability, validation, or root authority.

Supported profiles:

```text
ams_<sol|terra|luna>_<low|medium|high|xhigh|max>
ams_spark_<low|medium|high>
```

Profiles select the requested model family and reasoning effort. They do not grant sandbox, approval, network, tool, writable-root, or other permission overrides; those remain inherited from the platform, user, and current work order.

Route by failure cost, ambiguity, architecture/security impact, dependencies, novelty, verifiability, repetition, coupling, investigation depth, and supervisory burden:

- **Spark**: bounded text-only mechanics requiring little judgment; always a leaf.
- **Luna**: explicit, repetitive, low-risk, inexpensive-to-retry work.
- **Terra**: normal implementation, tests, documentation, review, and moderate investigation/management.
- **Sol**: ambiguous, novel, architectural, security-sensitive, cross-component, difficult, or expensive-to-fail work.

Effort: `low` for tight straightforward work; `medium` for ordinary multi-step work; `high` for dependencies and edge cases; `xhigh` for difficult investigation/design/validation; `max` for the hardest bounded exhaustive work. File count alone is not a strength signal.

Immediately before dispatch, verify the final selected profile. After each successful non-root spawn, immediately report the new session's task name and requested AMS capability profile; batch simultaneous spawns in one concise line and never present requested configuration as observed runtime identity.

For weak or failed work, correct the order before retrying; raise effort when the family remains suitable; escalate Luna→Terra→Sol by task character; and never repeat an unchanged setup.

## Task graph, work orders, and hierarchy

Maintain objective/criteria, dependencies, ready/active/completed/blocked/superseded work, physical identity when observable, logical parent/role/authority, ownership, required validation, selected profile, and outstanding results.

Each non-root session receives one compact stable-ID order:

```text
WORK ORDER
ID:
Root objective ID:
Logical parent: <root | work-order ID>
Orchestration role: <delegated-manager | worker>
Delegation authority: <request | none>
Temporary project role:
Capability profile:
Objective:
Scope / Excluded scope / Dependencies:
Tools, permissions, write ownership, transient artifacts, user-work constraints:
Authoritative context and prior decisions:
Required actions / Success criteria / Validation:
Expected execution profile / Deviation triggers / Return requirements:
```

Require:

```text
RESULT
Work-order ID / Logical parent / Orchestration role:
Status: complete | partial | blocked | failed
Execution identity: requested=<profile/model/effort>; observed=<when observable>
Summary / Evidence / Files-artifacts changed / Validation performed:
Deviations / Unresolved issues / Assumptions / Risks:
Recommended logical-parent action:
```

A direct worker uses `worker`/`none`. A delegated manager uses `delegated-manager`/`request` and follows `hierarchy-control.md`. Worker and manager completion are claims; only the root decides project completion.

Allow one active writer per mutable surface across the logical tree. Prefer disjoint paths or isolated workspaces; serialize shared manifests, schemas, interfaces, migrations, indexes, locks, and authoritative state. Preserve user changes. A non-root Git/history operation requires exact work-order authority and excludes all AMS controls and profiles.

## Operating loop and completion

Until the user objective is complete or genuinely blocked:

1. refresh the objective, dependencies, effective settings, active topology, ownership, and selected profiles;
2. select the smallest useful ready topology and issue non-overlapping work orders;
3. monitor progress, process bounded manager requests, and correct deviations;
4. collect results through logical parents, reconcile conflicts, and commission required integration;
5. apply user/project-required validation and accept or reject evidence;
6. close completed or superseded sessions and continue with the next required work.

If `project_governance = true`, apply `project-governance.md` for AMS-added project-wide acceptance criteria, proportional independent review, continuous-delivery posture, deviation handling, and continuity. If false, do not load that reference or impose its additional lifecycle/review requirements; follow the user's objective and authoritative project workflow while retaining core root authority, truthful evidence, ownership, work-order, hierarchy, model/effort, and safety controls.

A local failure is not automatically a project failure. Classify scope, context, profile/effort, permissions, ownership, tools, or external blockers; correct or reroute through bounded sessions. Never evade safety restrictions or claim unrun validation passed.

Declare complete only when the user/project-defined objective and required checks are satisfied, required results are reconciled, no mandatory work or live conflicting writer remains, and any enabled governance requirements are met. Otherwise report blocked with the exact blocker and next action. Do not expose private chain-of-thought.
