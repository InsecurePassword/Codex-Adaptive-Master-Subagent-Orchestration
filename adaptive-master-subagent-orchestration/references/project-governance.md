# AMS project governance

Read completely when `project_governance = true`, or in named-capability-only mode when a direct current-turn instruction explicitly invokes AMS review, convergence, or rejected-approach handoff despite governance being off. Named mode applies only that capability plus mandatory core controls; it does not enable the full lifecycle layer.

Governance does not change root authority, physical spawning, adaptive routing, hierarchy, permissions, or one-writer safety.

## Lifecycle and evidence

Maintain deliverables, mandatory acceptance criteria, dependencies, critical path, integration order, validation, risks, blockers, and status. Respect authoritative project-native packets, pauses, approvals, issue trackers, test gates, records, and capability controls. AMS coordinates agents; it does not override project authorization.

Continue known safe in-scope work. Stop for a genuine external blocker, unresolved material intent, unauthorized destructive/irreversible/external action, a materially different required choice, convergence intervention, or direct user instruction.

Require risk-proportional evidence: commands/exit codes, diffs, receipts, tests, builds, lint/type checks, reproductions, artifacts, documentation consistency, and security/architecture/regression review. Lower-cost output does not reduce verification.

Use a separate normally read-only reviewer for high-risk implementation, security-sensitive work, architecture, broad refactors, difficult defects, or manager integration when practical. A project-native review mechanism supersedes AMS review control. Otherwise load `review-control.md` only when `review_control = true` or explicitly overridden for this objective; without it, use proportional governance review without that optional addendum. Review is non-recursive.

The root reconciles findings, commissions missing checks, and accepts or rejects. A phase, commit, checkpoint, clean workspace, test pass, empty worker set, manager completion, or handoff is not project completion while mandatory work remains.

## Convergence and deviation

Treat unauthorized scope, ownership, parentage, delegation, destructive action, reduced validation, unchanged failure, nonconverging review/repair, optional post-acceptance work, or inconsistent completion claims as deviations. `runtime-core.md` owns detection. Load `convergence-control.md` only for its state, status, finalization, or response routes. A trusted project-native convergence/closure mechanism supersedes AMS. Once response custody begins, preserve it until terminal disposition or explicit convergence override.

Generic completion language never suppresses convergence. An override must explicitly name AMS convergence, a limit, or the disclosed intervention boundary.

## Continuity and handoff

Use authorized project-native continuity when present; otherwise provide completed work, evidence, active/blocked items, ownership, exact next action, and resumption condition. Load `handoff-control.md` only when `rejected_approach_handoff = true` or explicitly overridden, useful, and not superseded.

When a convergence tracking record exists, include campaign ID, epoch, correction/redesign counts and limits, candidate receipt, state, and record location. Package-local convergence tracking/history is the only AMS-specific durable runtime state; it is not a task database or general recovery ledger.
