# AMS logical hierarchy control

Read completely only when `runtime-core.md` selects a delegated-manager topology, processes a manager dispatch request/result, relays descendant evidence, or changes manager custody. If this reference is unavailable, flatten safely to direct workers or fail closed for manager behavior; never improvise a hierarchy.

## Authority and eligibility

All sessions may remain physical children of the root. Logical hierarchy is recorded by work-order lineage. The root is the sole physical spawn authority and owns global routing, topology, controls, integration decisions, acceptance, completion, and user communication. A worker is a leaf. A delegated manager owns only its assigned subgraph, may perform its bounded project work, and may request—but never independently spawn—root-mediated descendants.

The role/authority pairing is exact: `worker`/`none` or `delegated-manager`/`request`. A manager order must add to the runtime-core baseline:

```text
Effective intensity / Allowed descendant shape:
Delegable scope:
Descendant allocation: <finite root-recorded concurrency and/or operation/usage bounds>
Escalation/evidence target:
```

Because non-root sessions never read this reference, the root must copy the applicable compact dispatch-request and manager-result field requirements below into each manager order's return requirements; never forward the full reference or noisy transcript.

Authority, permissions, scope, ownership, and allocation may narrow but never expand down the chain. `minimal` permits only the serial root-plus-one procedure defined below. `balanced` permits only one active shape from `intensity-control.md` and no nested manager. Other modes impose no AMS-defined logical-depth or team-shape ceiling, but every layer must add real supervision, context isolation, or useful parallelism.

## Allocation and dispatch

Each accepted descendant consumes or partitions its parent's allocation. For count-based allocation, the descendant session consumes one unit before any child-manager suballocation; all downstream allocation is carved from the remaining total, never duplicated. A child manager receives no more than the unallocated remainder. Replenishment requires a new root decision. Allocation constrains activity, not logical depth.

A manager requests a descendant with:

```text
DISPATCH REQUEST
Root objective / Request ID / Parent work-order ID:
Requested role and proposed logical lineage:
Objective, scope, exclusions, dependencies:
Suggested profile, permissions, ownership:
Requested descendant allocation and delegable scope: <manager only>
Success criteria, validation, and delegation value:
```

The root verifies request-ID uniqueness/idempotency, lineage, scope, ownership, dependencies, allocation, mode, capacity, routing, safety, and value, then accepts, narrows, reroutes, delays, flattens, or rejects. Exact request replays return the recorded decision; conflicting ID reuse or duplicate dispatch is deviation. The root assigns the work-order ID and records the order, lineage, ownership, and allocation before physical spawn. An accepted request consumes/partitions the record exactly once. If spawn fails, record the failure and release ownership/allocation only after proving no session started.

## Custody and results

Every non-root order has exactly one immutable logical parent. Replacements always use new IDs. A parent change closes/supersedes the old order and issues a new ID; never rewrite lineage in place. Sessions may remain physical root children while reporting logically to a manager.

The root records each result idempotently by work-order ID and relays descendant results/evidence to the logical parent without accepting them on the manager's behalf. Exact duplicates reuse the recorded result; conflicting duplicates are deviation. A late result from a closed/superseded order remains evidence only and cannot restore ownership, status, or acceptance without explicit reconciliation. Cancellation, quarantine, or replacement releases ownership/allocation only after session closure and no live writer are proven; until then the slot remains occupied.

Managers must collect and reconcile descendant evidence before claiming their subgraph complete. Uncollected, conflicting, inaccessible, or orphaned work cannot support completion. A manager result adds:

```text
MANAGER RESULT ADDENDUM
Descendant requests/orders and status:
Evidence accepted/rejected/superseded/outstanding:
Remaining descendant allocation:
Ownership returned / Recommended logical-parent action:
```

Physical results normally flow through the logical parent unless immediate safety requires root intervention. If the parent is unavailable, preserve evidence and resume it or issue a new superseding manager order with explicit custody transfer; never invent acceptance. Completed evidence retains its original lineage. Any live descendant needing a new supervisor must be closed/superseded and reissued under a new work-order ID and logical parent. Under `minimal`, a manager may record a request and close, one worker runs, then the same manager session is resumed or a new superseding manager order is issued for review—never more than one non-root session at once.

## Completion, blocks, and ownership

Completion is hierarchical: worker completion is a leaf claim; manager completion is a validated-subgraph claim; only root completion is project completion. A local block affects one session; a chain block affects one manager subgraph after authorized reroutes are exhausted; a project block requires no compliant route for mandatory objective progress. Independent lanes continue through delegation when safe.

A manager may accept/reject descendant evidence for its assigned subgraph, but root acceptance remains mandatory. Root integration/acceptance cannot be delegated. Ownership is explicit and exclusive for every mutable surface. Managers coordinate ownership only within their subgraph and cannot transfer it outside granted scope. On closure, cancellation, replacement, or transfer, ownership is released only after the root proves no live writer remains.

## Deviation and recovery

Deviation includes unauthorized delegation, lineage mutation, circular/orphaned ancestry, duplicated/allocation amplification, conflicting request-ID reuse, accepting uncollected evidence, acting outside scope/ownership, parent substitution without supersession, or claiming project completion.

On deviation, stop dependent dispatch, let safe atomic work reach a boundary, preserve evidence, classify the defect, and choose the smallest safe response: reject/narrow request, close/cancel/replace, flatten/deepen/resequence, reconcile result, transfer custody by superseding order, or pause for unresolved authority/safety. Never repair hierarchy by editing old lineage in place.
