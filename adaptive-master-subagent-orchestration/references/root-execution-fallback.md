# AMS root execution fallback

Read completely only when standard `runtime-core.md` has determined that mandatory progress would otherwise stop, no currently viable delegated route remains, and effective `root_execution_fallback = true`.

This is a last-resort continuity control, not a normal execution mode. Higher-priority instructions remain authoritative. For an affected campaign under active convergence control, this reference is ineligible until convergence terminates `failed` or `blocked`, archives its state, and explicitly releases custody. `intervention-required` does not authorize fallback.

## Viable delegated route

A route is viable when it is currently spawnable, authorized, equipped with the required tools and permissions, ownership-compatible, expected to complete and validate the task, and expected to use fewer total tokens after context transfer, likely retries, and validation.

A slower route remains viable. Root speed alone never justifies fallback.

Do not exhaust tokens proving every hypothetical route impossible. Consider the materially distinct currently available routes and allow at most one corrected attempt per route unless new evidence warrants another.

## Eligibility

Root execution is permitted only when:

1. the action is mandatory for objective progress;
2. no viable lower-cost delegated route remains;
3. the action is already authorized and requires no new approval;
4. the action is low-risk and reversible when it mutates state;
5. it is not destructive, irreversible, externally visible, or security-sensitive;
6. no live or potentially live writer owns the affected surface;
7. the smallest atomic action can restore progress or a viable delegated route.

## Ownership and receipt

Before a mutation:

1. close, quarantine, cancel, or supersede the affected execution order;
2. prove that its writer is no longer live;
3. preserve original lineage and late-result rules;
4. reclaim the surface in the root task graph;
5. record temporary root-fallback ownership.

After the atomic mutation, bind validation to the exact result. Prefer an existing repository-native receipt such as a commit, diff, worktree snapshot, content hash, or immutable artifact that identifies the fallback action, affected paths, and validation target. Until that receipt exists, keep the affected surface write-frozen. Afterward, another writer may modify those paths only by explicitly superseding the pending fallback result; validation of a superseded receipt cannot accept later combined state.

Represent the affected work with the existing task model as `active` or `blocked` on independent validation. `implemented_pending_independent_validation` may be used only as a report label, not as a new canonical task state. Release or reassign ownership only after the receipt/freeze rule above is satisfied.

## Execution

Record concisely:

```text
Root fallback:
Blocker:
Unavailable or unsuitable delegated routes:
Atomic action:
Ownership and safety basis:
Output bound:
Receipt or freeze:
Required validation:
```

Use targeted reads, bounded search results, limited file ranges, and bounded command output. Redirect bulky output only to an authorized transient location, keep it out of Git, retain it only while needed for the next routing or validation action, and delete it after evidence is extracted or superseded.

Perform one atomic fallback unit per blocker episode, then return immediately to management and reassess delegation.

A second root-executed unit requires materially new evidence and a distinct new blocker. A continuation of the same implementation, test, integration, review, Git, deployment, or recovery lane is not a new episode.

Never repeat an unchanged failed fallback.

## Validation

A fallback mutation remains incomplete and blocked on independent validation of its exact receipt. The root may continue unrelated safe work but may not accept the affected surface from self-validation alone.

Final acceptance requires either:

- validation by a suitable non-root session against the exact receipt once one is viable; or
- explicit user acceptance of the documented residual risk.

This rule applies independently of `project_governance`.

Stop if scope expands, risk becomes material, ownership becomes uncertain, an approval is required, or the atomic endpoint is no longer clear. Never use fallback to evade safety policy, permissions, or project authorization.
