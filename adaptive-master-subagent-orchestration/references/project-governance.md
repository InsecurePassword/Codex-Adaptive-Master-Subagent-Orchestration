# AMS project governance

Read completely only when effective settings have `project_governance = true`. This optional layer adds project-wide workflow governance; it does not change Sol-root authority, physical spawn control, model/reasoning routing, work-order boundaries, hierarchy, permissions, or one-writer safety.

## Project lifecycle

Maintain explicit deliverables, mandatory acceptance criteria, dependencies, critical path, required integration order, validation obligations, risks, blockers, and ready/active/completed/superseded status. Respect authoritative project-native packet systems, pause gates, approvals, issue trackers, test gates, and recording requirements. AMS defines how agents are coordinated; it does not override what the project authorizes.

Continue useful authorized work without requiring another prompt while the next action is known, safe, in scope, and advancing. Stop only for a genuine external blocker, unresolved material user intent, destructive/irreversible/external action lacking authority, or a required choice between materially different paths.

## Evidence, validation, and review

Require evidence proportional to risk: commands and exit codes, diffs, tests, builds, linting, type checks, reproductions, artifact inspection, documentation consistency, and security/architecture/regression review when warranted. Lower-cost output remains evidence and does not reduce verification.

Use a separate normally read-only reviewer for high-risk implementation, security-sensitive work, architecture, broad refactors, difficult defects, or manager integration when practical. Review is proportional and non-recursive; do not repeat review without new evidence.

The root reconciles conflicting findings, commissions missing checks, and decides acceptance. A phase, commit, checkpoint, clean workspace, test pass, empty worker set, manager completion, or handoff is not project completion while mandatory work remains.

## Deviation and continuity

Treat unauthorized scope, ownership, parentage, delegation, destructive action, reduced validation, repeated unchanged failure, optional work after acceptance, or inconsistent completion claims as deviations. Let safe atomic work reach a boundary, preserve evidence, apply the smallest correction, and continue independent safe lanes.

Use existing authorized project-native state when durable continuity is required. Otherwise provide a concise user-visible handoff containing completed work, evidence, active/blocked items, ownership, exact next action, and resumption condition. The rule is explicit: never create an AMS-specific recovery file.
