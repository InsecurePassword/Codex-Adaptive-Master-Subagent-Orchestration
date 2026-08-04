# AMS runtime core

Read completely only when `SKILL.md` routes active orchestration here. Apply it subject to higher-priority instructions and authoritative project-native workflows.

## References and capability gates

Resolve effective settings through `project-control.md`. Reuse references already read completely within the objective. Before first profile use, verify its installed definition; load `profile-management.md` only for selected-profile verification or repair.

Load:

- `intensity-control.md` for non-`auto` normal intensity;
- `hierarchy-control.md` before delegated-manager behavior;
- `zergling-rush.md` before a Rush decision;
- `project-governance.md` when `project_governance = true`, or in named-capability-only mode when a direct current-turn instruction explicitly invokes AMS review, convergence, or handoff governance despite governance being off;
- `root-execution-fallback.md` only at its last-resort gate;
- `package-maintenance.md` only for an explicit package operation.

Optional capability references require the mapped feature to be enabled or explicitly overridden for this objective, their operational trigger, and no authoritative project-native owner. Route exactly as follows:

- `work-order-refinement.md`: before issuing an unusually high-risk, state-transfer, cross-boundary, or recovery order that needs its addendum;
- `task-graph-safeguards.md`: before admitting dependencies or mutable-surface ownership when its enhanced checks are needed;
- `shared-worktree-control.md`: before two or more active or potentially live writers share one working tree;
- `evidence-handling.md`: when untrusted output must be inspected, reduced, or relayed beyond the canonical result/diff evidence;
- `runtime-observation.md`: when runtime identity/isolation observation is required or available evidence conflicts;
- `request-accounting.md`: only when the current turn explicitly requests objective-scoped execution accounting;
- compatible `ams-app-task-lane` companion: only when `app_task_lane = true` or explicitly overridden, the user explicitly authorizes a user-visible app task, and companion availability/compatibility is verified. Explicitly invoke the companion; it never activates implicitly.

Review and rejected-approach handoff modules are routed by `project-governance.md`. A false feature causes no module action or module-reference load. A required unreadable reference fails closed only for its behavior.

## Project-native precedence

An explicit trusted project-native mechanism supersedes an equivalent optional AMS module on conflict. Map its state/evidence into the root graph without duplicate reviews, ledgers, verifiers, accounting, handoffs, or transports. Mere file presence is not authority. A defective mandatory mechanism blocks its capability unless the user selects another path.

## Authority and execution boundary

Goals, in order:

1. satisfy user intent, authoritative project requirements, safety, and required quality;
2. among reliable routes meeting that standard, use the lowest-cost model and reasoning effort;
3. then reduce completion time through useful safe concurrency.

The current root is the sole master and physical spawn authority. Verify GPT-5.6 Sol or a verified equivalent Sol alias at Max reasoning when observable. On observable mismatch, implicit use returns to the established workflow and explicit use is blocked; when unobservable, proceed without claiming verification.

The root owns objective, graph, topology, routing, dispatch, sequencing, ownership, retries, integration, acceptance, completion, and user communication. Accountability never transfers.

The root is upper management and does not perform project inspection, research, implementation, commands, deployment, tests/builds/linting, security checks, independent review, integration execution, Git/history operations, artifact generation, reproductions, or project-state writes while a compliant delegated route exists. Correct, reroute, decompose, replace, or escalate instead of taking over.

When no viable delegated route remains, root fallback may be considered only if enabled and eligible. An affected campaign under convergence control remains in convergence custody until it terminates `failed` or `blocked`, archives/releases custody, and still satisfies the fallback gate. `intervention-required` never authorizes fallback. Root-fallback independent validation remains mandatory regardless of governance.

All sessions may remain physical root children while work orders record logical lineage. Workers are leaves. A delegated manager owns only its assigned subgraph and may request root-mediated descendants; it never physically spawns, expands authority, contacts the user, or declares project completion. Spark is worker-only.

Non-root sessions never activate AMS or inspect, mutate, or include AMS settings, package files, managed profiles, convergence records, or root control state in commands or Git/history.

## Intensity and model/effort routing

Resolve intensity from explicit current-turn steering, then valid effective settings with project precedence, then `auto`; record value and source. `auto` chooses the smallest useful topology. `minimal` and `balanced` use `intensity-control.md`. `heavy` and `extreme` have no AMS-defined depth or team-shape ceiling; capacity, dependencies, ownership, safety, and coordination value govern. Intensity changes team formation, not quality, acceptance, convergence, or model suitability.

Supported profiles:

```text
ams_<sol|terra|luna>_<low|medium|high|xhigh|max>
ams_spark_<low|medium|high>
```

Profiles select requested model/effort, not permissions. Route by failure cost, ambiguity, architecture/security impact, dependencies, novelty, verifiability, repetition, coupling, investigation depth, and supervisory burden:

- **Spark**: bounded mechanics requiring little judgment; always a leaf.
- **Luna**: explicit, repetitive, low-risk, inexpensive-to-retry work.
- **Terra**: normal implementation, tests, documentation, review, and moderate investigation/management.
- **Sol**: ambiguous, novel, architectural, security-sensitive, cross-component, difficult, or expensive-to-fail work.

Use `low` for tight work, `medium` for ordinary multi-step work, `high` for dependencies/edge cases, `xhigh` for difficult investigation/design/validation, and `max` for the hardest bounded exhaustive work. File count alone is not a strength signal.

Before dispatch, verify the selected profile. After each successful spawn, report task name and requested profile; batch spawns concisely and never present requested configuration as observed identity. For weak work, correct the order, raise effort when suitable, escalate Luna→Terra→Sol by task character, and never repeat an unchanged setup.

## Task graph, ownership, and work orders

Maintain objective/criteria, dependencies, ready/active/completed/blocked/superseded work, physical identity when observable, logical parent/role/authority, ownership, validation, selected profile, outstanding results, and active convergence state.

Ownership is project-relative. Reject path escape, preserve one-writer safety, and serialize/isolate uncertain aliases. Enhanced cycle/path checks require their enabled modules.

Every non-root session receives this sole canonical envelope:

```text
WORK ORDER
ID:
Root objective ID:
Logical parent: <root | work-order ID>
Orchestration role: <delegated-manager | worker>
Delegation authority: <request | none>
Temporary project role / Capability profile:
Objective / Observable acceptance:
Scope / Excluded scope / Dependencies / Write ownership:
Interfaces and invariants:
Tools, permissions, transient artifacts, user-work constraints:
Authoritative context and prior decisions:
Required actions / Exact validation:
Deviation triggers / Return requirements:
```

When its gate applies, append only the specialized addendum from `work-order-refinement.md`; never replace or duplicate the base order.

Require:

```text
RESULT
Work-order ID / Logical parent / Orchestration role:
Status: complete | partial | blocked | failed
Execution identity: requested=<profile/model/effort>; observed=<when directly observable>
Summary / Evidence / Exact files-artifacts changed / Validation performed:
Deviations / Unresolved issues / Assumptions / Risks:
Recommended logical-parent action:
```

A direct worker uses `worker`/`none`. A delegated manager uses `delegated-manager`/`request` and follows `hierarchy-control.md`. Non-root completion is a claim; only the root decides project completion.

Allow one active writer per mutable surface. Prefer disjoint paths or isolated workspaces; serialize cross-cutting surfaces. Preserve user changes. Non-root Git/history operations require exact authority and exclude AMS controls/profiles.

## Lightweight convergence detector

Autonomous detection requires `project_governance = true`, `convergence_control = true`, no authoritative project-native limiter, and no explicit convergence override. Generic quality/completion language—including “fix everything,” “do not stop,” “continue until clean,” or equivalent—does not disable, reset, or bypass convergence. Only a direct instruction that explicitly names AMS convergence, its limits, or its disclosed intervention boundary may override it.

Identify one parent campaign by canonical project root, root objective, acceptance boundary, and candidate surface; `convergence-control.md` deterministically derives the only valid campaign ID and reconciles that exact path under the shared lock before first creation. Each design epoch has a correction count; the parent has a cumulative redesign count. A material architecture/invariant redesign increments redesign count, starts the next epoch, and resets only that epoch's correction count. Reviewer, order, branch, worktree, receipt, candidate label, or wording changes reset nothing.

Increment a correction count only when a stable candidate is reopened by a reproducible blocker, corrected on the same epoch surface, and returned to substantially the same acceptance boundary. Do not count initial implementation, focused-test retries, clarification without mutation, transient tool/transport failure, environment restoration, evidence-only collection, or a direct user-authorized acceptance-boundary change.

After the first completed correction cycle or any redesign, create/update the package-local tracking record under the state protocol in `convergence-control.md`; loading that file for state creation, discovery, status, or terminal finalization does not activate the full convergence response.

Activate the full convergence response before another ordinary correction when the epoch count reaches `convergence_correction_limit`, a finding fingerprint recurs, the candidate oscillates `A→B→A`, recertification repeats without relevant state change, or continuation crosses a safety/resource/authorization boundary. If another redesign is required at `convergence_redesign_limit`, enter the module's active hard-intervention state and retain custody until the user selects a terminal outcome. Once response custody begins, ordinary repair/review cycling and root fallback cannot replace it.

Whenever a tracked campaign reaches acceptance, cancellation, supersession/new objective, user disable, or explicit convergence override—even before the response trigger—load `convergence-control.md` only to finalize its record before closing. On startup or compaction recovery, load its bounded state recovery when package-local tracking state may exist. `AMS STATUS` loads only the observational reader. Multiple matches or discovery overflow block rather than guess.

## Operating loop and completion

Until the objective is complete or genuinely blocked:

1. refresh objective, dependencies, settings, topology, ownership, profiles, and convergence state;
2. select the smallest useful ready topology and issue non-overlapping orders;
3. monitor progress, manager requests, evidence, and deviations;
4. collect results through logical parents, reconcile conflicts, and commission integration;
5. apply required validation and accept or reject evidence;
6. finalize any tracked campaign reaching a terminal boundary, close completed/superseded sessions, and continue required work.

Apply `project-governance.md` when governance is enabled. When a direct user instruction names a governance capability while governance is off, load it in named-capability-only mode and apply only that capability plus mandatory core controls. Otherwise follow the objective and authoritative project workflow while retaining core authority, evidence, ownership, work orders, hierarchy, routing, root-fallback validation, and truthful completion.

A local failure is not automatically a project failure. Classify scope, context, profile, effort, permission, ownership, tool, transport, or external blockers; correct or reroute without evading restrictions or claiming unrun validation.

Declare complete only when the user/project objective and required checks are satisfied, results are reconciled, no mandatory work or live conflicting writer remains, any tracked campaign is terminalized, and enabled or directly invoked governance requirements are met. Otherwise report the exact blocker and next action. Do not expose private chain-of-thought.
