# AMS Daybreak Blue cyber fallback

Read completely only when `runtime-core.md` has evidence that the Sol root received an explicit cyber-safeguard refusal—during root handling or from a standard Sol non-root execution order—for a still-required authorized defensive cybersecurity task and is deciding whether to use the optional Daybreak Blue route. This is not a normal model-selection reference.

## Purpose and qualifying trigger

Daybreak Blue is a root-spawned, worker-only fallback for one unchanged authorized defensive cybersecurity work unit that standard Sol could not complete because of cyber safeguards. It is not a stronger general Sol tier, an offensive lane, a permission bypass, an authorization substitute, or a reason to pre-route ordinary security work away from Sol.

The root may consider `ams_daybreak_blue_max` only when all are true:

1. the task is lawful, authorized defensive cybersecurity work on systems, applications, accounts, networks, code, artifacts, or data the user owns, operates, or is explicitly authorized to test or analyze;
2. the work fits the approved defensive purpose, such as Secure SDLC/AppSec, secure review or patching, threat modeling or intelligence, threat hunting, malware or suspicious-code analysis, detection engineering, vulnerability triage or validation, incident response, or patch validation;
3. the root has an explicit refusal or blocked-completion message attributable to cyber safeguards from root handling or a standard Sol `worker` or `delegated-manager`, rather than weak, cautious, partial, or incorrect work;
4. the still-required bounded work can be retried without expanding targets, authority, permissions, actions, data handling, or operational impact;
5. no higher-priority instruction, safety rule, authorization boundary, ownership conflict, project-native control, or Trusted Access/data-governance boundary independently prohibits it.

Do not trigger Daybreak for a timeout, transport/capacity failure, missing file or context, unavailable tool, sandbox or approval denial, network restriction, profile defect, account/quota error, unsupported effort, quality failure, ordinary inability, or non-cyber refusal. Never infer target authorization or Trusted Access from the installed profile.

## Frozen fallback unit and refusal provenance

Assign one stable `Daybreak fallback unit ID` to the frozen objective, target, scope, exclusions, authorization basis, data boundary, and operational boundary. Equivalent refusals from retries, replication, replacement, resumed work, or reparenting map to the same unit. A material boundary change creates a new work unit and requires fresh routing; it never renews the earlier unit.

Record:

```text
Daybreak fallback unit ID:
Attempt state: not-started | active | consumed
Refusal source: root-handling | work-order
Original Sol work-order ID: none-root-handling | <stable work-order ID>
Original Sol role: root | worker | delegated-manager
Original logical parent: root | <work-order ID>
Refusal evidence ID:
```

`none-root-handling` is the only valid work-order sentinel for a root-origin refusal. Store only a small exact excerpt or faithful bounded summary of the refusal with unrelated sensitive data removed.

## Canonical access-route record

Route availability is not owned by an individual fallback unit. The root owns one canonical `Daybreak route record` for each normalized access context and current Codex session generation.

Build its deterministic, non-secret key from:

```text
Provisioned access path
Execution surface
Approved identity or membership basis
Approved organization/workspace/project boundary
Internal-only status
Retention requirement and coverage
Exact installed Daybreak profile SHA-256
Requested model and effort
Codex signed-in session generation ID
```

Record:

```text
Daybreak route record ID:
Route generation:
Route disposition: unverified | verifying | verified | closed-unavailable
Reserved fallback unit ID: none | <ID>
Verification operation ID:
Verification attempt: 0 | 1 | 2
Route evidence ID:
Route blocker:
Reopen condition:
Verified binding: <fallback unit ID / logical parent / custody state / intensity shape | none>
```

Rules:

- All units with the same normalized key reference the same route record.
- Treat the route record as single-flight: permit only one active verification or Daybreak task reservation. Other units wait; they do not start parallel probes.
- Verification is one-time admission for the reserved unit only. It is not reusable by another unit, logical parent, custody state, intensity shape, root objective, or Codex session generation.
- Keep the record `verified` and reserved while the admitted task is pending or active. After that task reaches a terminal state, clear the reservation and return the route to `unverified` unless an authoritative route/capability failure requires `closed-unavailable`.
- `closed-unavailable` applies to every unit referencing that route record and survives work-order replacement, reparenting, compaction, handoff, root replacement, and recovery.
- Reopen a closed record only by creating a new generation after explicit new provisioning evidence or an explicit user-directed recheck following a material access-context change.
- Accept verification results only when the route generation, verification operation ID, reserved unit ID, logical parent, and nonce match the current record. A stale or late result is evidence only. It cannot overwrite a newer generation or reopen `closed-unavailable`.
- If any key field changes or cannot be proven unchanged, invalidate verification and create a new `unverified` generation. Never carry verified state across a different signed-in session generation.

When durable continuity is required, preserve the complete route record and each referencing fallback unit in an existing authorized project-native record or the user-visible handoff required by `project-control.md` or `project-governance.md`. Never create an AMS-specific recovery file.

## Provisioned access path and data-governance gate

Before verification or task dispatch, establish this non-secret context without recording credentials, tokens, secrets, or unnecessary personal data:

```text
Provisioned access path: codex-workspace | api-organization | user-or-model-specific
Execution surface: codex-interactive | codex-security-plugin | codex-cli | codex-github-action | responses-api | approved-codex-api-workflow | exact-provisioned-surface
Approved identity or membership basis:
Approved organization/workspace/project boundary:
Internal-only use confirmed: yes
Retention requirement: standard-approved-surface | ZDR | custom
Retention coverage: confirmed | not-required-beyond-standard
Retention evidence ID:
Provisioning/onboarding evidence ID:
Codex signed-in session generation ID:
Access-context fingerprint:
```

Compatibility is exact:

| Provisioned access path | Permitted execution surface | Required boundary |
|---|---|---|
| `codex-workspace` | A named Codex surface explicitly covered by onboarding, such as `codex-interactive`, `codex-security-plugin`, `codex-cli`, or `codex-github-action` | The named internal Codex or ChatGPT organization/workspace |
| `api-organization` | `responses-api` or an explicitly approved `approved-codex-api-workflow` | The named internal API organization/project and credentials scoped to it |
| `user-or-model-specific` | Only `exact-provisioned-surface` as stated by OpenAI | The exact confirmed identity and boundary; use `none-user-level` only when the provisioning confirmation explicitly states that no organization/workspace/project applies |

Do not combine workspace and API approval in one route record. When both are provisioned, create separate normalized records. Reject an API-organization approval used through an unapproved direct Codex workspace surface, a workspace approval used through an unapproved API project, an undocumented sentinel, or any other incompatible pair.

Evidence may be platform-observed metadata, an approved onboarding record, or explicit current user confirmation tied to the active signed-in identity and surface. A profile file, model catalog entry, installation, prior session, or absence of an error is not proof.

Fail closed before verification when the access path, execution surface, identity, boundary, internal-only status, signed-in session generation, or required retention treatment cannot be established. When ZDR or custom retention is required, coverage must be confirmed for the exact boundary and surface. `not-required-beyond-standard` is valid only when that workflow accepts the standard terms of the exact approved surface.

## Lineage, custody, ownership, and allocation

Every Daybreak session is a physical root child with exact role/authority `worker`/`none`. Physical root dispatch does not force logical parent `root`.

Resolve custody before verification:

- **Root-handling refusal:** logical parent `root`; no prior non-root writer is implied.
- **Sol worker refusal:** close or supersede the refused order, prove no prior worker remains live, and preserve its logical parent in new verification/task work-order IDs. Transfer project-surface ownership only after capability verification.
- **Sol delegated-manager refusal in `balanced`, `heavy`, `extreme`, or authorized Rush:** the manager remains logical parent, relinquishes execution ownership of the affected surface, and does not write it concurrently.
- **Sol delegated-manager refusal in `minimal`:** the manager records the refusal, verification/task request, and evidence target; relinquishes ownership; reaches a useful boundary; and closes. Mark its immutable order `inactive-resumable`. Run the standard-Sol control when required, Daybreak capability verification, and Daybreak task serially as the only active non-root session. After task closure, resume that manager or issue a superseding manager order under `hierarchy-control.md` for reconciliation.
- **Genuinely unavailable parent or deliberate flattening:** use the existing explicit supersession and custody-transfer procedure. An intentionally inactive `minimal` parent is not unavailable.

Record original/current parent, custody state (`active | inactive-resumable | superseded`), custody decision, prior-writer closure, allocation, and intensity-shape decision. Every verification/control/task session consumes an ordinary worker slot while active. Preserve one-writer safety. Physical delivery to the root is transport; task evidence is reconciled through the logical parent or explicit superseding custodian.

## Capability-verification preflight

A Daybreak task may start only after the canonical route record is `verified` and bound to that exact fallback unit, logical parent, custody state, intensity shape, access context, profile hash, model/effort, and session generation.

Reserve the route record to the unit before any probe. The verification work order is data-minimized and receives no project files, repository content, telemetry, malware sample, credentials, secrets, customer data, refusal excerpt, target details, project ownership, Git authority, mutation authority, network collection authority, or live-target interaction.

Use one of these proof modes:

1. **Platform-attested:** the platform exposes and the root records effective Daybreak access identity for the exact approved path and surface.
2. **OpenAI validation workflow:** use the current bounded defensive validation workflow supplied through OpenAI onboarding on the exact approved surface.
3. **Differential synthetic fixture:** use one public or organization-approved, non-project, local-only defensive fixture with explicit expected results. The identical fixture must first receive a qualifying cyber-safeguard refusal from standard Sol in the current root/session generation. If standard Sol completes it or only produces weak/partial output, it is not distinguishing and cannot verify Daybreak.

A synthetic fixture must contain no user/customer data, live target, credentials, working malware payload, persistence/stealth step, exploit chain, external side effect, or deployment instruction. It may use static toy code or inert artifacts for defensive triage, patching, IOC extraction, detection logic, or vulnerability validation. Record the fixture ID/version, source, expected result, reviewer, and standard-Sol control result when required.

The Daybreak verification work order adds:

```text
Daybreak operation: capability-preflight
Daybreak route record ID / generation:
Reserved fallback unit ID:
Verification operation ID / nonce:
Verification attempt: 1 | 2
Capability proof mode:
Fixture ID/version/source and expected result:
Standard-Sol control result ID: <ID | not-required-platform-attested | not-required-openai-workflow>
Access context and evidence IDs:
Logical parent / custody state / intensity shape:
Requested route: profile=ams_daybreak_blue_max; model=gpt-daybreak-blue-latest; effort=max
Observed route: <value when platform-observable | unavailable>
Project data supplied: no
Project ownership supplied: none
```

The session returns the universal AMS `RESULT` plus:

```text
DAYBREAK CAPABILITY PREFLIGHT ADDENDUM
Daybreak route record ID / generation:
Reserved fallback unit ID:
Verification operation ID / nonce:
Capability proof mode:
Fixture ID/version and expected-result status:
Standard-Sol control result ID:
Requested route:
Observed route: <value | unavailable>
Profile contract accepted: yes | no
Worker role confirmed: worker/none
Project or customer data accessed: no
Project mutation or target interaction performed: no
Result-return path operational: yes | no
Capability criteria satisfied: yes | no
Blocker:
```

The root validates normal result custody plus the exact generation, operation ID, nonce, unit binding, proof mode, fixture/control evidence, expected result, role, and no-data/no-mutation claims. Set `verified` only when all required criteria pass. A nonce echo alone proves transport and is never sufficient capability evidence.

### Verification attempt budget

Permit at most two Daybreak process-start attempts per route generation:

1. the initial verification attempt;
2. one retry only when the first failure is proven to have occurred before any Daybreak session started and is classified as temporary transport or capacity failure.

A confirmed start, uncertain start/result, malformed or non-distinguishing result, failed expected criterion, refusal, substitution, model/effort mismatch, entitlement/access failure, wrong context, or second no-start failure closes the route as `closed-unavailable`. Do not retry automatically. A material access/provisioning change requires explicit new evidence and a new route generation; it is not a retry.

## Task-attempt dispatch

After verification, recheck the exact installed profile hash, route generation/binding, access context, custody, ownership, and `Attempt state = not-started`. Only then transfer project ownership and the minimized task context.

The task work order adds:

```text
Daybreak operation: task-attempt
Daybreak route record ID / generation:
Daybreak fallback unit ID:
Attempt transition: not-started -> active on confirmed start -> consumed on terminal result
Route disposition: verified
Verification operation/evidence ID:
Capability proof mode and fixture/control ID:
Access context and evidence IDs:
Refusal provenance:
Original/current logical parent and custody state:
Prior-writer closure and ownership transfer:
Allocation and intensity-shape decision:
Authorized defensive purpose and authorization basis:
Frozen objective, target, scope, exclusions, data boundary, and operational boundary:
Attempt budget: 1 of 1
Requested route: profile=ams_daybreak_blue_max; model=gpt-daybreak-blue-latest; effort=max
Observed route: <value when observable | unavailable>
```

Pass only the data needed for the unchanged frozen task. The worker may deepen analysis, finish a defensive patch, or produce the originally requested defensive evidence. It may not add targets, broaden access, increase persistence or stealth, introduce credential acquisition, operationalize an attack beyond the authorized defensive objective, or deploy against a live target.

On confirmed start, set the unit to `active`. If start is uncertain, retain `active` and prohibit another attempt until closure is proven. A task proven not to have started releases ownership/allocation and leaves `not-started`; the route record remains governed independently.

Every terminal result after confirmed start—complete, partial, blocked, failed, refused, unusable, lost, or cancelled—sets `consumed`. Do not repeat, fan out, rotate profiles, reset through replacement/reparenting/recovery, or escalate automatically to Daybreak Red, another cyber-specialized model, an offensive workflow, or root execution. Extreme and Rush do not increase the budget.

Require normal `RESULT` plus:

```text
DAYBREAK RESULT ADDENDUM
Daybreak operation: task-attempt
Daybreak route record ID / generation:
Daybreak fallback unit ID:
Attempt state at return: consumed
Verification evidence and capability proof mode:
Access context:
Original and final logical parent / custody state:
Custody, ownership, and allocation preserved: yes | no
Requested route:
Observed route: <value | unavailable>
Trusted Access/data boundary preserved: yes | no
Qualifying trigger honored: yes | no
Frozen scope preserved: yes | no
Authorization or boundary concerns:
Residual refusal, access-path, or capability blocker:
```

Daybreak output is evidence, not acceptance. Relay it through the logical parent or superseding custodian, reconcile it with the original objective, and commission normal independent validation when required. After terminal task handling, release the route reservation and return the route record to `unverified` unless authoritative evidence requires `closed-unavailable`.

If the bounded fallback cannot complete safely within the contract, report the exact blocker and stop.
