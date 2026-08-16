# AMS Daybreak Blue cyber fallback

Read completely only when `runtime-core.md` has evidence that the Sol root received a cyber-safeguard refusal—during root handling or from a standard Sol non-root execution order—for a still-required authorized defensive cybersecurity task and is deciding whether to use the optional Daybreak Blue route. This is not a normal model-selection reference.

## Purpose and qualifying trigger

Daybreak Blue is a root-spawned, worker-only, one-attempt fallback for authorized defensive cybersecurity work whose unchanged bounded objective was blocked by a standard Sol cyber safeguard. It is not a stronger general Sol tier, an offensive lane, a permission bypass, an authorization substitute, or a reason to pre-route ordinary security work away from Sol.

The root may select `ams_daybreak_blue_max` only when all are true:

1. the task is lawful, authorized defensive cybersecurity work on systems, applications, accounts, networks, code, artifacts, or data the user owns, operates, or is explicitly authorized to test or analyze;
2. the work fits the approved defensive purpose, such as Secure SDLC/AppSec, secure code review and patching, threat modeling, threat intelligence, threat hunting, malware or suspicious-code analysis, detection engineering, vulnerability triage or validation, incident investigation/response, or patch validation;
3. the Sol root received an explicit refusal or blocked-completion message attributable to cyber safeguards, either during root handling or from a standard Sol non-root execution order whose role was `worker` or `delegated-manager`, rather than merely receiving weak, cautious, partial, or incorrect work;
4. the original bounded work remains required and can be retried without expanding targets, authority, permissions, actions, or operational impact;
5. no higher-priority instruction, safety rule, authorization boundary, ownership conflict, or project-native control independently prohibits the work.

Do not trigger Daybreak Blue for a timeout, transport or capacity failure, missing file, missing context, unavailable tool, sandbox or approval denial, network restriction, profile defect, account/quota error, unsupported reasoning effort, quality failure, ordinary inability, or a refusal unrelated to cyber safeguards. A request for clarification, a warning, a scoped limitation, or a partial answer is not itself a qualifying refusal. Do not infer authorization from Daybreak access.

## Stable fallback unit and refusal provenance

Before any Daybreak dispatch, assign one stable `Daybreak fallback unit ID` within the root objective. Bind it to the frozen objective, target, scope, exclusions, authorization basis, and operational boundary—not to a transient source work-order ID. Materially equivalent refusals from replicated, replacement, resumed, or reparented Sol orders map to the same unit. A material change to any frozen boundary creates a new work unit and requires fresh routing; it does not renew the earlier unit.

Record the unit in the live root task graph with this attempt state:

```text
not-started | active | consumed
```

Use these exact provenance values:

```text
Refusal source: root-handling | work-order
Original Sol work-order ID: none-root-handling | <stable work-order ID>
Original Sol role: root | worker | delegated-manager
Original logical parent: root | <work-order ID>
Refusal evidence ID: <stable root-recorded identifier>
```

`none-root-handling` is the only valid work-order sentinel for a refusal received during root handling. For a work-order refusal, the ID, role, and original logical parent must match the recorded Sol order. Store only a small exact excerpt or faithful bounded summary of the refusal and remove unrelated sensitive content.

When durable continuity is required, preserve the fallback unit ID, frozen boundary, provenance, and current attempt state in an existing authorized project-native record or the user-visible handoff required by `project-control.md` or `project-governance.md`. Never create an AMS-specific recovery file.

## Lineage, custody, ownership, and allocation

Daybreak Blue is always a physical child of the root and has the exact role/authority pair `worker`/`none`. “Root-spawned” describes physical dispatch; it does not force the logical parent to be `root`.

Resolve logical custody before dispatch:

- **Root-handling refusal:** use logical parent `root`. No prior non-root writer is implied.
- **Sol worker refusal:** close or supersede the refused order, prove that no prior worker remains live, and issue a new Daybreak work-order ID with the same logical parent. Preserve the existing surface ownership only through an explicit transfer recorded by the root.
- **Sol delegated-manager refusal:** the manager remains the logical parent and relinquishes execution ownership of the refused surface. The root dispatches Daybreak as that manager's worker descendant. The manager may supervise and reconcile the result but may not write the same surface concurrently.
- **Unavailable logical parent:** resume the parent or use the explicit supersession and custody-transfer procedure in `hierarchy-control.md` before Daybreak dispatch. Never rewrite parentage in place or bypass manager review silently.
- **Deliberate flattening:** close or supersede the prior chain, issue new IDs, transfer custody explicitly under `hierarchy-control.md`, and prove that no conflicting writer remains.

The Daybreak worker consumes one ordinary non-manager worker slot and the applicable finite allocation. Under `balanced`, preserve the already selected direct-worker or manager shape; do not mix shapes to make room for Daybreak. Serialize the replacement or record a valid finite allocation decision under the existing intensity and hierarchy rules. Under every mode, allow one active writer per mutable surface.

Return Daybreak evidence through the recorded logical parent. Physical delivery to the root is transport only; it does not bypass logical-parent reconciliation or give the worker project-completion authority.

## Dispatch and route-evidence contract

Use only the canonical `ams_daybreak_blue_max` profile and preserve every ordinary runtime-core ownership, one-writer, permission, validation, evidence, and Git-authority control.

The compact work order must add:

```text
Daybreak fallback unit ID:
Attempt transition: not-started -> active on successful spawn -> consumed on terminal result
Daybreak fallback trigger: qualifying cyber-safeguard refusal
Refusal source: root-handling | work-order
Original Sol work-order ID: none-root-handling | <stable work-order ID>
Original Sol role: root | worker | delegated-manager
Original logical parent: root | <work-order ID>
Custody decision and current logical parent:
Prior writer closure and ownership-transfer evidence:
Allocation and intensity-shape decision:
Refusal evidence ID and bounded evidence:
Authorized defensive purpose and authorization basis:
Frozen objective, target, scope, exclusions, and operational boundary:
Attempt budget: 1 of 1 for this Daybreak fallback unit
Requested route: profile=ams_daybreak_blue_max; model=gpt-daybreak-blue-latest; effort=max
Observed route: <value when observable | unavailable>
```

The frozen objective must be materially identical to the refused work unit. Pass only the context and data required to complete that work. The fallback may deepen analysis, finish a defensive patch, or produce the originally requested defensive evidence, but it must not add targets, broaden access, increase persistence or stealth, introduce credential acquisition, operationalize an attack beyond the authorized defensive objective, or convert analysis into deployment against a live target.

Before spawn, verify the effective profile bytes and requested model route under `profile-management.md`. Exact canonical bytes establish the requested configuration only. A successful spawn using the selected profile with no explicit platform mismatch, entitlement error, or access-path error is sufficient requested-route evidence to begin work; it is not independent attestation of the effective model. Record observed identity when the platform exposes it. When identity is unobservable, record `observed=unavailable`, proceed without claiming observation, and do not require the worker to self-attest.

An explicit model mismatch, wrong approved organization/workspace or product surface, entitlement failure, or access-path failure blocks Daybreak execution. Record the exact blocker and stop the route. Do not repeatedly probe, alter credentials, change permissions, or substitute an unchanged standard route.

## Attempt state, result, and acceptance

Immediately before physical dispatch, require the unit state to be `not-started` and reserve its ownership and allocation. On a confirmed successful spawn, set it to `active`. If it is uncertain whether a session started, retain `active` and prohibit another attempt until closure is proven. A failed spawn proven not to have started releases ownership/allocation and leaves the state `not-started`; an authoritative account or access-path unavailability still closes the fallback route without automatic re-probing.

A terminal Daybreak result—complete, partial, blocked, failed, refused, unusable, lost after confirmed start, or cancelled after start—sets the unit to `consumed`. Do not repeat the unchanged prompt, rotate profiles, split or replicate the same unit across multiple Daybreak workers, reset the unit because a work-order ID or logical parent changed, or escalate automatically to Daybreak Red, a cyber-specialized model, an offensive workflow, or root execution. Extreme and Zergling Rush do not increase this budget.

Require the normal `RESULT` plus:

```text
DAYBREAK RESULT ADDENDUM
Daybreak fallback unit ID:
Attempt state at return: consumed
Refusal source and original Sol work-order ID:
Original and final logical parent:
Custody, ownership, and allocation preserved: yes | no
Requested route:
Observed route: <value | unavailable>
Qualifying trigger honored: yes | no
Frozen scope preserved: yes | no
Authorization or boundary concerns:
Residual refusal, access-path, or capability blocker:
```

Daybreak output is evidence, not automatic acceptance. The root relays it through the logical parent, reconciles it with the original objective, and commissions ordinary independent validation when required and safely possible. A validator uses normal routing unless that distinct validation work independently receives its own qualifying standard-Sol refusal and is assigned its own stable fallback unit. Any mutation remains subject to existing ownership and project-governance acceptance rules.

If the bounded fallback cannot complete safely and within scope, report the exact blocker to the root and stop.
