# AMS Daybreak Blue cyber fallback

Read completely only when `runtime-core.md` has evidence that the Sol root received a cyber-safeguard refusal—during root handling or from a standard Sol non-root execution order—for a still-required authorized defensive cybersecurity task and is deciding whether to use the optional Daybreak Blue route. This is not a normal model-selection reference.

## Purpose and qualifying trigger

Daybreak Blue is a root-spawned, worker-only, one-attempt fallback for authorized defensive cybersecurity work whose unchanged bounded objective was blocked by a standard Sol cyber safeguard. It is not a stronger general Sol tier, an offensive lane, a permission bypass, an authorization substitute, or a reason to pre-route ordinary security work away from Sol.

The root may select `ams_daybreak_blue_max` only when all are true:

1. the task is lawful, authorized defensive cybersecurity work on systems, applications, accounts, networks, code, artifacts, or data the user owns, operates, or is explicitly authorized to test or analyze;
2. the work fits the approved defensive purpose, such as Secure SDLC/AppSec, secure code review and patching, threat modeling, threat intelligence, threat hunting, malware or suspicious-code analysis, detection engineering, vulnerability triage or validation, incident investigation/response, or patch validation;
3. the Sol root received an explicit refusal or blocked-completion message attributable to cyber safeguards, either during root handling or from a standard Sol non-root execution order whose role was `worker` or `delegated-manager`, rather than merely receiving weak, cautious, partial, or incorrect work;
4. the original bounded work remains required and can be retried without expanding targets, authority, permissions, actions, data handling, or operational impact;
5. no higher-priority instruction, safety rule, authorization boundary, ownership conflict, project-native control, or Trusted Access/data-governance boundary independently prohibits the work.

Do not trigger Daybreak Blue for a timeout, transport or capacity failure, missing file, missing context, unavailable tool, sandbox or approval denial, network restriction, profile defect, account/quota error, unsupported reasoning effort, quality failure, ordinary inability, or a refusal unrelated to cyber safeguards. A request for clarification, warning, scoped limitation, or partial answer is not itself a qualifying refusal. Never infer target authorization or Trusted Access from the presence of the profile.

## Stable fallback unit and route record

Before any Daybreak dispatch, assign one stable `Daybreak fallback unit ID` within the root objective. Bind it to the frozen objective, target, scope, exclusions, authorization basis, data boundary, and operational boundary—not to a transient source work-order ID. Materially equivalent refusals from replicated, replacement, resumed, or reparented Sol orders map to the same unit. A material change to any frozen boundary creates a new work unit and requires fresh routing; it does not renew the earlier unit.

Record the task-attempt state separately from route availability:

```text
Attempt state: not-started | active | consumed
Route disposition: unverified | verifying | verified | closed-unavailable
Access-context ID:
Route-evidence ID:
Route blocker:
Reopen condition:
```

`Route disposition` is root-owned state for the exact non-secret Trusted Access context. `closed-unavailable` survives work-order replacement, logical reparenting, compaction, handoff, root replacement, and recovery. Reopen it only after explicit new provisioning evidence or an explicit user-directed recheck following a material access-context change. Do not reopen it merely because a session, work-order ID, logical parent, or root changed.

When durable continuity is required, preserve the fallback unit ID, frozen boundary, access-context ID, route disposition and evidence, blocker/reopen condition, refusal provenance, custody decision, and attempt state in an existing authorized project-native record or the user-visible handoff required by `project-control.md` or `project-governance.md`. Never create an AMS-specific recovery file.

## Trusted Access and data-governance gate

Before a Daybreak preflight or task attempt, the root must establish the exact approved access and data-handling context without recording credentials, tokens, secrets, or unnecessary personal data:

```text
Trusted Access scope: user-level | named workspace | API organization/project
Approved identity or membership basis:
Approved organization/workspace/project:
Approved product surface: Codex
Internal-only use confirmed: yes
Retention requirement: standard approved-surface terms | ZDR | custom
Retention coverage: confirmed | not-required-beyond-standard
Retention evidence ID:
Provisioning/onboarding evidence ID:
Access-context ID:
```

The evidence source may be platform-observed metadata, an approved onboarding record, or explicit current user confirmation tied to the active signed-in identity and surface. A profile file, model catalog entry, successful installation, prior session, or absence of an error is not sufficient by itself.

Fail closed before sending task data when the active identity, organization/workspace/project, product surface, internal-only status, or required retention treatment cannot be established. If ZDR or custom retention is required, `Retention coverage` must be `confirmed` for the exact organization/project and product surface. `not-required-beyond-standard` is valid only when the approved workflow accepts the standard data controls and retention terms of that exact surface.

Pass the specialized worker only the non-secret context fields and evidence identifiers needed to enforce the boundary. Daybreak never grants broader local access, network reach, credentials, target authority, or permission to collect unrelated data.

## Refusal provenance

Use these exact provenance values:

```text
Refusal source: root-handling | work-order
Original Sol work-order ID: none-root-handling | <stable work-order ID>
Original Sol role: root | worker | delegated-manager
Original logical parent: root | <work-order ID>
Refusal evidence ID: <stable root-recorded identifier>
```

`none-root-handling` is the only valid work-order sentinel for a refusal received during root handling. For a work-order refusal, the ID, role, and original logical parent must match the recorded Sol order. Store only a small exact excerpt or faithful bounded summary of the refusal and remove unrelated sensitive content.

## Lineage, custody, ownership, and allocation

Daybreak Blue is always a physical child of the root and has the exact role/authority pair `worker`/`none`. “Root-spawned” describes physical dispatch; it does not force the logical parent to be `root`.

Resolve logical custody before any preflight or task attempt:

- **Root-handling refusal:** use logical parent `root`. No prior non-root writer is implied.
- **Sol worker refusal:** close or supersede the refused order, prove that no prior worker remains live, and issue new Daybreak work-order IDs with the same logical parent. Transfer project-surface ownership only after the access preflight succeeds and only through an explicit root record.
- **Sol delegated-manager refusal in `balanced`, `heavy`, `extreme`, or an authorized Rush topology:** the manager remains the logical parent and relinquishes execution ownership of the refused surface. The root dispatches the preflight and task attempt as that manager's worker descendants. The manager may supervise and reconcile results but may not write the same surface concurrently.
- **Sol delegated-manager refusal in `minimal`:** the manager records the refusal, preflight/task request, and evidence target; relinquishes execution ownership; reaches a useful boundary; and closes. Treat that intentionally inactive manager order as `inactive-resumable`, not unavailable. Run the access preflight alone, then the task attempt alone, while both retain the inactive manager order as immutable logical parent. After the task attempt closes, resume the same manager session when possible or issue a new superseding manager order under `hierarchy-control.md` to receive custody and reconcile the held result. Never have the manager and either Daybreak worker active concurrently.
- **Genuinely unavailable logical parent:** resume the parent or use the explicit supersession and custody-transfer procedure in `hierarchy-control.md` before dispatch. An intentionally inactive `minimal` parent following the serial procedure above is not unavailable.
- **Deliberate flattening:** close or supersede the prior chain, issue new IDs, transfer custody explicitly under `hierarchy-control.md`, and prove that no conflicting writer remains.

Record:

```text
Original logical parent:
Current logical parent:
Logical-parent custody state: active | inactive-resumable | superseded
Custody decision:
Prior-writer closure evidence:
Allocation and intensity-shape decision:
```

Each Daybreak worker consumes one ordinary non-manager worker slot and the applicable finite allocation while active. Under `balanced`, preserve the selected direct-worker or manager shape; do not mix shapes. Under `minimal`, use the serial procedure above. Under every mode, allow one active writer per mutable surface.

Physical delivery to the root is transport only. Task-result evidence must be relayed through the recorded logical parent or its explicit superseding custodian before acceptance. The root owns route selection and may validate the data-free preflight receipt directly; under the `minimal` serial procedure it holds that receipt for later parent relay while setting the route disposition needed to run the task alone.

## Mandatory data-free access preflight

A Daybreak task attempt may start only when `Route disposition = verified` for the exact `Access-context ID`. If no current verified route evidence exists, perform one data-free preflight after the qualifying refusal and before transferring project ownership or task data.

The preflight:

- uses the exact `ams_daybreak_blue_max` profile, `gpt-daybreak-blue-latest`, and `max` effort;
- uses the planned task's logical parent and intensity shape;
- receives no project files, repository content, telemetry, malware sample, credentials, secrets, customer data, refusal excerpt, or task implementation details;
- receives no project-surface write ownership or Git authority;
- performs no project inspection, command execution, mutation, network collection, or target interaction;
- carries one root-generated verification ID and nonce;
- does not consume the fallback unit's one task-attempt budget.

The preflight work order adds:

```text
Daybreak operation: access-preflight
Daybreak fallback unit ID:
Route disposition transition: unverified -> verifying
Access-context ID:
Trusted Access context: <non-secret gate fields and evidence IDs>
Verification ID:
Verification nonce:
Logical parent and custody state:
Allocation and intensity-shape decision:
Requested route: profile=ams_daybreak_blue_max; model=gpt-daybreak-blue-latest; effort=max
Observed route: <value when observable | unavailable>
Project data supplied: no
Project ownership supplied: none
```

Require:

```text
DAYBREAK ACCESS PREFLIGHT RESULT
Daybreak fallback unit ID:
Verification ID:
Verification nonce:
Logical parent:
Requested route:
Observed route: <value | unavailable>
Profile contract accepted: yes | no
Worker role confirmed: worker/none
Project data accessed: no
Project mutation performed: no
Result-return path operational: yes | no
Blocker:
```

Set `Route disposition = verified` only after a confirmed successful spawn returns to the root with the exact verification ID and nonce, confirms the worker-only contract, and confirms no project data or mutation. The root validates this routing-control receipt. Normally it relays the receipt through the recorded logical parent immediately; under the `minimal` serial procedure it may hold the receipt until the inactive-resumable manager is resumed after the task, because no project result is being accepted and the root alone owns route selection. This proves the requested Codex custom-agent path and result-return path for the current access context; it is not independent attestation of an unobservable effective model.

A preflight mismatch, malformed receipt, entitlement error, wrong access context, unsupported model/effort, access-path failure, confirmed substitution, or uncertain start/result closes the route as `closed-unavailable` and records the evidence ID, blocker, and reopen condition. Do not retry automatically. A temporary transport/capacity failure proven not to have started may return the disposition to `unverified`, but it still permits no task data until a later successful preflight.

A prior verified result may be reused only while the exact access context, selected profile bytes, model/effort route, signed-in identity basis, organization/workspace/project, product surface, and retention treatment remain unchanged and the evidence survives in the current root state or authorized continuity record.

## Task-attempt dispatch contract

After successful preflight, verify the effective profile bytes under `profile-management.md`, require `Route disposition = verified`, require `Attempt state = not-started`, reserve allocation, and only then transfer project ownership and the minimized task context.

The compact task work order must add:

```text
Daybreak operation: task-attempt
Daybreak fallback unit ID:
Attempt transition: not-started -> active on successful spawn -> consumed on terminal result
Route disposition: verified
Access-context ID:
Route-evidence ID and successful preflight verification ID:
Trusted Access context: <non-secret gate fields and evidence IDs>
Daybreak fallback trigger: qualifying cyber-safeguard refusal
Refusal source: root-handling | work-order
Original Sol work-order ID: none-root-handling | <stable work-order ID>
Original Sol role: root | worker | delegated-manager
Original logical parent: root | <work-order ID>
Current logical parent and custody state:
Custody decision:
Prior writer closure and ownership-transfer evidence:
Allocation and intensity-shape decision:
Refusal evidence ID and bounded evidence:
Authorized defensive purpose and authorization basis:
Frozen objective, target, scope, exclusions, data boundary, and operational boundary:
Attempt budget: 1 of 1 for this Daybreak fallback unit
Requested route: profile=ams_daybreak_blue_max; model=gpt-daybreak-blue-latest; effort=max
Observed route: <value when observable | unavailable>
```

Pass only the data required to complete the frozen work. The fallback may deepen analysis, finish a defensive patch, or produce the originally requested defensive evidence, but it must not add targets, broaden access, increase persistence or stealth, introduce credential acquisition, operationalize an attack beyond the authorized defensive objective, or convert analysis into deployment against a live target.

Exact canonical profile bytes and the successful data-free preflight establish requested-route evidence only. Record observed identity when the platform exposes it. When identity is unobservable, record `observed=unavailable`, proceed without claiming observation, and do not require worker self-attestation. An explicit route mismatch or changed access context invalidates the preflight, blocks task dispatch, and returns to the route-disposition rules above.

## Attempt state, result, and acceptance

On a confirmed successful task spawn, set `Attempt state = active`. If it is uncertain whether the task worker started, retain `active` and prohibit another attempt until closure is proven. A task spawn proven not to have started releases project ownership/allocation and leaves `Attempt state = not-started`; route disposition remains governed independently.

A terminal task result—complete, partial, blocked, failed, refused, unusable, lost after confirmed start, or cancelled after start—sets `Attempt state = consumed`. Do not repeat the unchanged prompt, rotate profiles, split or replicate the same unit across multiple Daybreak task workers, reset the unit because a work-order ID or logical parent changed, or escalate automatically to Daybreak Red, a cyber-specialized model, an offensive workflow, or root execution. Extreme and Zergling Rush do not increase this budget.

Require the normal `RESULT` plus:

```text
DAYBREAK RESULT ADDENDUM
Daybreak operation: task-attempt
Daybreak fallback unit ID:
Attempt state at return: consumed
Route disposition and access-context ID:
Preflight verification ID:
Refusal source and original Sol work-order ID:
Original and final logical parent:
Logical-parent custody state:
Custody, ownership, and allocation preserved: yes | no
Requested route:
Observed route: <value | unavailable>
Trusted Access/data boundary preserved: yes | no
Qualifying trigger honored: yes | no
Frozen scope preserved: yes | no
Authorization or boundary concerns:
Residual refusal, access-path, or capability blocker:
```

Daybreak output is evidence, not automatic acceptance. The root relays it through the logical parent or explicit superseding custodian, reconciles it with the original objective, and commissions ordinary independent validation when required and safely possible. A validator uses normal routing unless that distinct validation work independently receives its own qualifying standard-Sol refusal and is assigned its own stable fallback unit. Any mutation remains subject to existing ownership and project-governance acceptance rules.

If the bounded fallback cannot complete safely and within scope, report the exact blocker to the root and stop.
