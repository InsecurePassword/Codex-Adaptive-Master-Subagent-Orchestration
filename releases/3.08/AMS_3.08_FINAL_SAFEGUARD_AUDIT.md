# Adaptive Master–Subagent Orchestration 3.08

## Final Safeguard Remediation Audit

**Source artifact:** `adaptive-master-subagent-orchestration-3.07-final-safeguard-audited(1).zip`

## Audit posture

The 3.07 package was treated as third-party work. Previous reports and claims of correction were not trusted. Every runtime file was read from beginning to end, the behavioral state machine was reconstructed from the files, all literal and semantic references were checked, the package was compared with the original architecture and stated goals, and adversarial scenarios were exercised by inspection. Findings were repaired in the package, after which the audit was restarted against the modified 3.08 files.

This is a static behavioral and structural audit. It did not execute live Codex child sessions or simulate operating-system race conditions unavailable in this environment.

## Runtime inventory

| File | Lines | Bytes | Role |
|---|---:|---:|---|
| `SKILL.md` | 26 | 5,450 | Root guard, reference trust boundary, activation router, lazy loading |
| `VERSION` | 1 | 5 | Package version token (`3.08`) |
| `agents/openai.yaml` | 6 | 298 | UI metadata and implicit-invocation eligibility |
| `references/intensity-control.md` | 14 | 2,081 | Normal manual intensity gates |
| `references/profile-management.md` | 154 | 18,652 | Conditional profile generation, migration, repair, validation |
| `references/project-control.md` | 107 | 16,837 | Settings, steering, Spark cache, durable state, recovery |
| `references/runtime-core.md` | 149 | 23,074 | Authority, routing, work orders, safety, orchestration, terminal rules |
| `references/zergling-rush.md` | 66 | 5,653 | Current-consent experimental high-consumption mode |
| `references/package-maintenance.md` | 27 | 4,287 | Lazy package identity, mutation, rollback, and reload controls |

All files are UTF-8 without BOM, LF-only, final-LF terminated, contain no NUL bytes, and remain below their reference size limits. YAML and frontmatter parse. The project default TOML parses to the exact schema-2 disabled defaults.

## Reconstructed behavior

1. Child sessions exit before resolving AMS settings or references.
2. Every packaged reference crosses a root-contained, regular-file, no-redirect, identity-stable, bounded UTF-8 trust boundary before being loaded as instructions.
3. A trusted project with missing settings receives the exact disabled default; initialization does not activate AMS. Untrusted, rootless, invalid, disabled, or non-implicit settings fail closed.
4. Explicit invocation can run in memory; implicit invocation requires product metadata, project trust, project enablement, and project implicit permission.
5. Sol Max remains the sole control-plane authority; project execution is delegated to direct non-delegating children.
6. Normal routing is cost-first Spark → Luna → Terra → Sol at the lowest reliable effort.
7. Auto, minimal, moderate, heavy, and extreme preserve their intended dispatch postures.
8. Zergling Rush requires current-turn user selection for every activation; repository persistence is only a stored preference.
9. Profile management is lazy, provenance-constrained, backed up, atomic, and recognizes original, v3.0.0, 3.07, and current schemas.
10. Package maintenance is lazy and exclusive, preserves the active contract through update, validates candidate and installed identity, rolls back failures, and requires reload after behavior changes.
11. Work orders, execution identity, one-writer ownership, child exclusion from AMS controls, evidence, independent review, deviation supervision, recovery, continuity, and complete-versus-blocked terminal states remain.

## Remediations

### F-01 — Persisted Rush consent — Resolved

Repository-controlled settings no longer constitute consent. Every Rush activation requires an unambiguous current-turn user instruction. A persisted Rush value is a preference only; without current confirmation, the objective uses in-memory `auto` or retains its current non-Rush mode.

### F-02 — v3 Spark migration and sandbox schema — Resolved

Profile provenance now separately recognizes:

- current Sol/Terra/Luna five-field schema;
- current Spark six-field schema with `sandbox_mode = "workspace-write"`;
- official v3 Sol/Terra/Luna five-field profiles;
- actual official v3 Spark six-field profiles;
- prior 3.07 schema-1 Spark five-field profiles through an exact description/model/effort/instruction signature;
- original marker-only profiles and the historical runner under their prior narrow signatures.

Current Spark generation includes the approved workspace-write sandbox override, and validation rejects unrelated behavior-changing fields.

### F-03 — Missing project settings — Resolved

In a trusted project with a stable root, the router loads project control and atomically creates the exact disabled schema-2 default. Creation itself never enables AMS and ordinary implicit processing stops afterward. Untrusted, trust-indeterminate, and rootless contexts are never mutated.

### F-04 — Package maintenance in routine context — Resolved

Package identity, fingerprinting, candidate validation, rollback, directory replacement, mixed-generation recovery, uninstall behavior, and reload transitions were moved into `references/package-maintenance.md`.

Normal runtime context fell from 30,851 bytes in 3.07 to 28,524 bytes in 3.08 despite adding the initial reference trust boundary. The 4,287-byte maintenance contract is loaded only for package operations, integrity suspicion, post-change reload state, or package-dependent recovery.

### F-05 — Initial reference trust gap — Resolved

`SKILL.md` now validates every reference before loading it as instructions: installed-root containment, maximum size, regular/non-redirected type, symlink/junction/reparse/multilink rejection, stable identity, UTF-8 without BOM/NUL, LF-only termination, and active-package identity matching when available. Known package mutation prevents loading changed instructions in the current session.

### Additional finding — 3.07 current-schema Spark migration — Resolved

The first remediation pass would have recognized v3.0.0 Spark files but not Spark profiles generated by 3.07 itself, which used `profile-schema: 1` without `sandbox_mode`. An exact 3.07 legacy signature and contract were added so those files can be safely backed up and upgraded without aliases or repeated mismatch discovery.

### Additional finding — Subagent guard ordering — Resolved

The reference trust check initially preceded the child-session guard. The guard now executes first, ensuring a child session performs no AMS settings or reference resolution.

## Original architecture and goal comparison

Preserved:

- Sol Max sole architecture, topology, routing, acceptance, and completion authority.
- Direct children only; no child delegation.
- Delegation-first project execution and narrow indeterminate-failure master fallback.
- Cost minimization first and useful concurrency second in normal modes.
- Spark-first mechanical routing and separate availability cache.
- Full Sol/Terra/Luna effort matrix and Spark Low/Medium/High.
- Task graph, stable work orders, requested/observed identity, distilled evidence, ownership, integration sequencing, and independent review.
- Deviation classification/correction, anti-loop policy, operator-intent handling, unattended continuation, exact-next-action persistence, recovery, anti-stall behavior, and terminal acceptance.
- Normal highest intensity named `extreme`; no confusing Sol-Ultra child profile or orchestration name appears.

No original non-bootstrap functionality was found missing after remediation.

## Break attempts

| Scenario | Result |
|---|---|
| Skill appears inside a child session | Exits before settings/reference resolution. |
| Trusted project has no settings | Creates exact disabled default, remains inactive. |
| Untrusted/rootless project has no settings | No write; implicit activation fails closed. |
| Reference is symlinked, redirected, oversized, malformed, or changes during read | Rejected before instruction loading. |
| Reference changes after package mutation | Current session retains pre-change contract and requires reload. |
| Trusted repository persists Rush | Does not activate Rush without current-turn confirmation. |
| Current turn explicitly selects Rush | Activates after warning; persistence still does not waive future confirmation. |
| Actual v3 Spark six-field profile | Recognized as managed legacy and upgraded with backup. |
| 3.07 schema-1 Spark five-field profile | Recognized by exact prior signature and upgraded with backup. |
| User-authored or ambiguous profile | Preserved; compatible profile reused or nonconflicting alias created. |
| Current Spark profile | Requires six fields including approved workspace-write sandbox. |
| Package update during active work | Requires quiescence, backup, atomic replacement/rollback, identity distinction, reload. |
| Package rollback fails | Package becomes unusable; ordinary dispatch stops with exact recovery action. |
| Clear child failure | Correction remains delegated. |
| Indeterminate failure with no viable child route | Narrow master fallback is allowed and reported. |
| Minimal mode has multiple active children | Stops new dispatch until one remains. |
| Extreme has more than 20 eligible lanes | No skill ceiling; actual capacity controls. |
| Mandatory blocker remains | Reports blocked, not complete. |

## Cross-reference audit

All literal paths resolve:

- `SKILL.md` → `project-control.md`, `runtime-core.md`
- `runtime-core.md` → `package-maintenance.md`, `profile-management.md`, `intensity-control.md`, `zergling-rush.md`, `project-control.md`
- `project-control.md` → `zergling-rush.md`, `package-maintenance.md`

All named semantic references exist, including `Registry and invariants`, `Exact purposes`, `Previous schema-1 Spark contract`, `Original marker-only child contract`, `Spark availability cache`, and runtime Sections 2–7.

## Final component condition

| Component | Condition |
|---|---|
| `SKILL.md` | **Healthy** |
| `VERSION` | **Healthy** |
| `agents/openai.yaml` | **Healthy** |
| `intensity-control.md` | **Healthy** |
| `profile-management.md` | **Healthy** |
| `project-control.md` | **Healthy** |
| `runtime-core.md` | **Healthy** |
| `zergling-rush.md` | **Healthy** |
| `package-maintenance.md` | **Healthy** |

## Verdict

**CLEAN under the completed static behavioral and structural safeguard audit.**

No release-blocking or material omission remains in the instruction package as reviewed. Live Codex/backend integration and operating-system race behavior remain environment-dependent and should be exercised by deployment/runtime tests when the package is installed.
