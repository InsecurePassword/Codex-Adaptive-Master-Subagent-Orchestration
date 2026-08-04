# AMS evidence-bound fresh review control

Read completely only when `review_control = true`, governance or the user has commissioned an independent review, no authoritative project-native review contract supersedes it, and the exact review candidate is ready. The setting alone never creates a review.

## Canonical envelope

Every reviewer receives the complete canonical `runtime-core.md` WORK ORDER with:

```text
Orchestration role: worker
Delegation authority: none
Temporary project role: independent reviewer
Write ownership: none
```

The order must include root objective, logical parent, selected capability profile, tools/permissions, exact review scope, and validation. Never replace the canonical order with a separate review envelope.

Append one review-specific block.

### Commitment review addendum

```text
REVIEW ADDENDUM
Review type: commitment
Decision receipt:
Proposed decision:
Alternatives considered:
Interfaces and invariants:
Decisive question:
Required verdict: proceed | change | stop
```

### Final review addendum

```text
REVIEW ADDENDUM
Review type: final
Change-set receipt:
Exact changed paths:
Interfaces and invariants:
Primary validation receipts:
Required review scope:
Required verdict: ship | fix-first | rethink
```

Use a fresh session without inherited turns. The reviewer is behaviorally read-only, receives no write ownership or delegation authority, and may not implement findings, alter the candidate, expand acceptance criteria, contact the user, or accept project completion.

## Evidence binding

Bind review to an immutable or identity-stable receipt: commit, Git tree, complete diff hash, artifact hash set, project-native candidate receipt, or exact proposal hash. Freeze or exclude competing writers on the reviewed surface. The reviewer must inspect actual files and evidence; a receipt is an identity boundary, not a substitute for inspection.

Any relevant mutation, changed artifact, superseding commit, changed-path set, or replacement validation invalidates the verdict and requires a fresh review.

## Canonical return

The reviewer returns the normal `RESULT` envelope, then appends:

```text
REVIEW RESULT ADDENDUM
Review type: commitment | final
Receipt reviewed:
Verdict: proceed | change | stop | ship | fix-first | rethink
Decisive reason:
Findings:
Residual risk:
```

Runtime route, sandbox, permission profile, and before/after mutation evidence are root-owned observations. The reviewer must not self-attest them. The root may load `runtime-observation.md` only through its feature gate.

## Isolation and acceptance

Profiles remain permission-neutral. Request behavioral read-only operation and record actual isolation only when directly observable. If the host grants broader access and hard isolation is not required, capture exact before-and-after state and accept the review only when no mutation occurred. If hard isolation is required but unavailable, or any mutation occurs, stop the review lane.

Treat the verdict as an evidence claim. For `fix-first`, issue a corrected implementation order to an authorized writer, rerun validation, create a new receipt, and commission a fresh review. For `rethink`, revise architecture or scope before continuing. Never convert a reviewer into an implementation lane.
