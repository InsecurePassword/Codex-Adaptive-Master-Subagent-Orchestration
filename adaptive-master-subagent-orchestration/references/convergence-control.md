# AMS convergence control

Read completely for one of four bounded purposes:

1. create or update tracking state after the first completed correction cycle or material redesign;
2. discover/read/reconcile state for startup, compaction recovery, handoff, or `AMS STATUS`;
3. finalize a tracked campaign at any terminal boundary, even when the full response never triggered;
4. execute the full convergence response after the detector in `runtime-core.md` triggers or the user directly invokes it.

State-only use does not activate the full response. A trusted project-native convergence, packet-closure, or defect-disposition mechanism supersedes this module on conflict.

## Purpose, authority, and user override

This module prevents a bounded packet from becoming an unbounded adversarial review-and-repair campaign. It changes methodology; it is not a defect quota, deadline, weaker validation, or authority to accept a known architecture, security, privacy, durability, correctness, or required-behavior defect.

A direct current-turn user instruction remains controlling authority. To override the automated guard, it must explicitly name AMS convergence, a convergence limit, or the disclosed intervention boundary and state the desired bypass/change. Generic completion or quality language—including “continue,” “fix everything,” “do not stop,” or “until no issues remain”—does not disable, reset, or bypass convergence.

Once the full response takes custody, no ordinary retry loop, speculative review expansion, app-task replacement, or root fallback replaces it. Intensity remains unchanged for topology decisions and unrelated work.

## Campaigns, epochs, and limits

Use the parent identity established by `runtime-core.md`: canonical project root + root objective + acceptance boundary + candidate surface. Normalize all four values to Unicode NFC and reject control characters. Use the already-established physical absolute project root, `/` separators, no redundant/trailing separator except a filesystem root, and case-fold only when that filesystem is proven case-insensitive. Use the exact stable root-objective ID, not objective prose. Prefer authoritative packet/checkpoint/receipt and surface IDs; otherwise trim and collapse ASCII whitespace in the boundary and surface labels. Encode exactly as `ams-convergence-campaign-v1\nproject_root<TAB>...\nroot_objective_id<TAB>...\nacceptance_boundary<TAB>...\ncandidate_surface<TAB>...\n`, and set `campaign_id = cvg-<lowercase SHA-256 of those UTF-8/LF bytes>`. Before first creation and under the shared lock, perform the complete bounded active-record search using these normalized fields. Reuse the exact deterministic path when present; if that path is absent but one safe legacy/nondeterministic record matches the same parent, reconcile that record instead of creating another; multiple matches, a conflicting deterministic path, or unsafe migration blocks. Never choose a random ID or create a second active record for one parent. Epoch 1 begins with `redesign_count = 0`. Each material architecture/invariant redesign:

1. increments `redesign_count`;
2. starts the next design epoch under the same parent;
3. resets only `epoch_correction_count`;
4. preserves cumulative findings, receipts, decisions, and history.

Reviewer, order, branch, worktree, receipt, label, or wording changes reset nothing. Another redesign is forbidden when `redesign_count >= convergence_redesign_limit`; enter `intervention-required`. With defaults, the initial design plus four redesigns allows at most five epochs and twenty ordinary correction cycles.

## Runtime paths and shared lock

Convergence is the only AMS capability authorized to create durable package-local runtime state:

```text
<skill-root>/.runtime/convergence/<campaign-id>.tracking.log
<skill-root>/.runtime/convergence/history/<campaign-id>.<terminal-receipt-sha256>.record.log
```

The shared package/runtime lock is outside the replaceable skill directory:

```text
<skill-parent>/.adaptive-master-subagent-orchestration.runtime.lock/
```

Every claim, update, finalization, stale reconciliation, history publication, export/import, install, update, repair, rollback, uninstall, or recovery read that may acquire custody must use this same lock. Lock order is always: shared package/runtime lock → tracking record generation check → immutable history publication. Never acquire another AMS package/runtime lock inside it. `AMS STATUS` is the sole lock-free exception: it performs only bounded identity-stable reads, creates no lock, and reports `state-changing` instead of guessing when two immediate metadata-and-byte snapshots differ.

The lock directory is owner-only (`0700` on POSIX; current user plus system/administrators only on Windows) and contains exactly one owner-only `owner.log` (`0600` or equivalent), at most 4 KiB, UTF-8/LF, with this exact order:

```text
ams-runtime-lock-v1
owner_id<TAB><[A-Za-z0-9._-]{1,128}>
purpose<TAB><installer|convergence|startup-recovery|runtime-export|runtime-import|package-maintenance>
campaign_id<TAB><campaign-id|none>
host_id<TAB><lowercase [a-z0-9._-]{1,128}>
pid<TAB><positive decimal|none>
acquired_epoch<TAB><non-negative decimal>
lease_expires_epoch<TAB><non-negative decimal>
```

Acquire by owner-only atomic directory creation, publish complete owner bytes promptly, then verify owner token and permissions. An unexpired lease reports the owner after at most a bounded wait. For an expired valid lease, automatic takeover is allowed only when `host_id` equals the current canonical lowercase host ID, the numeric PID is proven non-live, and the owner bytes remain unchanged before and after quarantine. A crash before `owner.log` publication is recoverable only after a 30-second initialization grace when the real directory remains unchanged across two one-second snapshots and contains no entries except at most one bounded owner-only `.owner.*` staging file; quarantine it before claiming. A foreign host, `pid = none`, malformed published record, live PID, changed snapshot/bytes, unexpected entry, failed quarantine, or ambiguous liveness blocks. Release only when the exact owner token still matches. Installers implement this same protocol and hold the lock from pre-snapshot through backup deletion.

## Record format, ownership lease, and generation fencing

Tracking and history directories/records are owner-only (`0700` directories and `0600` files on POSIX, or the Windows ACL equivalent defined above). Creation, atomic replacement, history publication, import, and installer restoration must set and verify those permissions. Records are bounded UTF-8/LF tab-delimited logs, not free-form prose or JSON, and contain no tabs/newlines/control characters inside values and no prompts, credentials, environment variables, private reasoning, or raw logs.

Active records begin exactly:

```text
ams-convergence-tracking-v1
```

and contain each key exactly once:

```text
campaign_id
root_objective_id
project_root
state
owner_id
owner_lease_expires_at
record_generation
created_at
updated_at
design_epoch_id
redesign_count
redesign_limit
epoch_correction_count
correction_limit
candidate_receipt
acceptance_boundary
candidate_surface
finding_fingerprints
last_resolution_action
```

Each later line is `key<TAB>value`. The file is at most 64 KiB; campaign ID is `[A-Za-z0-9._-]{1,96}` and matches the filename; counters/generation are non-negative decimal integers; timestamps are canonical UTC; values are bounded single-line text. Keep at most eight comma-separated SHA-256 finding fingerprints or `none`.

A tracking record is also the campaign ownership lease. Under the shared lock, claim only when no different unexpired owner exists. When an owner lease expires, verify no live owner/session when observable before takeover. Every mutation must read the expected `record_generation`, compare it under the lock, increment it exactly once, stage the complete next bytes, atomically replace, and verify. A generation mismatch means another writer won; discard the stale mutation and reload. Renew the owner lease before expiry while custody is active.

States are:

```text
monitoring
convergence
intervention-required
terminal-pending-history
```

## Immutable history and terminal finalization

History is one immutable record per terminal campaign, not a shared append log. A history record begins:

```text
ams-convergence-history-v1
```

contains the active fields plus:

```text
terminal_disposition
terminal_receipt
closed_at
```

and is published by an atomic no-overwrite move to `history/<campaign-id>.<terminal-receipt-sha256>.record.log`. Each record is at most 64 KiB. The terminal receipt is a SHA-256 digest over the bounded terminal facts and matches the filename. If an identical record already exists, publication is idempotent; a conflicting same-name record blocks. After durable publication and verification, delete the matching tracking record under the same lock.

Terminal dispositions are:

```text
accept
accept-with-follow-up
blocked
failed
cancelled
user-disabled
user-override
superseded
stale
```

Finalization applies whenever a tracked campaign closes, including pre-trigger acceptance/cancellation, a new user-defined objective, feature/governance disable, or explicit override. `intervention-required` is never terminal: it retains active custody until a direct user decision, then finalizes as the resulting `accept`, `accept-with-follow-up`, `user-override`, `cancelled`, `superseded`, `blocked`, or `failed` disposition. If history publication fails, set `terminal-pending-history`, release operational custody only when the chosen terminal outcome permits it, and report the maintenance blocker. Direct disable/override still takes effect. `AMS STATUS` only reports pending repair; the next top-level startup recovery performs publication/deletion and never resumes the record as active work.

Immutable per-campaign history removes global append saturation. History files are retained until explicit user-authorized archival/removal; installers preserve the exact safe layout.

## Bounded discovery, status, and compaction recovery

When the campaign ID is known, read only that exact safe file. Startup/recovery reads it under the shared lock; `AMS STATUS` requires two identical immediate file identity, size, timestamp, and byte snapshots. When context loss removed the ID, startup/recovery lists under the shared lock; status takes two identical bytewise directory-name snapshots before reading. In either path, sort safe `*.tracking.log` names bytewise. If more than 128 exist, stop with `discovery-overflow`; never inspect an arbitrary subset. Otherwise compare every record in this order:

1. exact normalized project root;
2. root objective ID when known;
3. candidate receipt, first qualifying work-order identity, or acceptance boundary;
4. current live ownership/session evidence.

Exactly one match may be reconciled. No match means no resumable campaign. Multiple plausible matches or discovery overflow block and are reported; never guess or read history as active state. `AMS STATUS` is strictly observational: it neither claims records nor publishes history. Startup recovery claims only through the lease/generation protocol.

For an expired record with no matching active objective and no live owner, startup recovery finalizes it `stale`. Startup recovery finalizes `terminal-pending-history` before any resume attempt. Handoff includes campaign ID, epoch/counts/limits, receipt, state, owner lease, and tracking path.

## Full convergence response

Stop new open-ended adversarial review and unchanged repair cycles. Let safe atomic work reach a useful boundary unless safety, ownership, authorization, or explicit user instruction requires immediate interruption.

### Stabilize

- Freeze candidate, complete diff, ownership, environment, and receipts.
- Collect useful evidence, then close duplicate speculative reviewers.
- Keep one shared-core writer; parallelize only disjoint work or bounded read-only analysis.
- Pin the validated toolchain; do not synchronize dependencies or alter locks/versions unless authorized.
- Record unrelated baseline failures once and move them to a separate authorized lane or explicit acceptance exclusion.

### Fix the acceptance boundary

Create one bounded contract:

```text
CONVERGENCE CONTRACT
Campaign / epoch / correction and redesign counts and limits:
Candidate receipt and mutable surface:
Required acceptance criteria:
Architecture, security, privacy, durability, and correctness invariants:
Blocking finding definition:
Known unrelated baseline failures:
Pinned environment and authoritative commands:
Focused adversarial checks:
One final authoritative suite:
Final bounded review scope:
Follow-up destination for nonblocking hardening:
```

A reviewer may discover evidence but may not silently add acceptance criteria. Classify each finding as `blocking-now`, `control/environment blocker`, `follow-up hardening`, or `duplicate/superseded/unproven`.

### Change the method

- Oscillating race patches: commission a bounded state-machine, ownership, happens-before, fencing, or transaction-boundary redesign.
- One shared mutable core: retain one writer and consolidate findings into one correction wave.
- Expanding review scope: use the fixed invariant checklist.
- Reviewer disagreement: commission one bounded evidence adjudication, not recursive reviewer review.
- Unrelated suite failures: establish one authoritative baseline and separate that cluster.
- Environment contamination: restore/verify the locked environment without dependency synchronization.
- Repeated broad suites: use focused correction checks and one authoritative suite after stabilization.

Route every lane through the lowest-cost model/effort that reliably meets quality; convergence does not imply Sol/Max everywhere.

### Execute one bounded resolution transaction

1. Consolidate blocking findings and root-cause evidence.
2. Perform one root-cause/architecture pass when the prior method is unstable.
3. Issue one corrected canonical work order or non-overlapping correction wave.
4. Run fixed focused adversarial checks.
5. Run one final authoritative suite in the pinned environment.
6. Perform one fresh bounded acceptance review against only the convergence contract. Use project-native review when authoritative; otherwise normal governance review, adding `review-control.md` only through its gate.

A deterministic localized regression introduced by the consolidated correction permits one localized correction, affected focused checks, and one repeated bounded acceptance review. It does not reopen broad adversarial discovery. A remaining same-class architecture defect may begin another design epoch only below the redesign limit; otherwise enter `intervention-required`.

## Custody and fallback

Accept only when the contract, focused checks, authoritative suite, and bounded review pass. Preserve legitimate nonblocking hardening in a forward packet, issue, or handoff instead of reopening the accepted transaction.

`blocked` or `failed` releases convergence custody only after terminal record publication or `terminal-pending-history` state with the exact blocker/receipt. The root may then evaluate `root-execution-fallback.md`; convergence failure is necessary but not sufficient, and fallback independent validation remains mandatory. `intervention-required` never releases to fallback without a direct user decision.
