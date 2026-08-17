# AMS profile management

Read completely only for profile selection, verification, deployment, or an explicitly requested profile operation. The package ships 19 canonical profiles under `assets/agent-profiles/`; installers deploy them to the effective Codex agent registry.

## Registry and names

Preferred registry: `$CODEX_HOME/agents/`. Use project-local `<project-root>/.codex/agents/` only when global profiles are unavailable, deliberate isolation is required, or authoritative project instructions require it.

Supported names:

```text
ams_<sol|terra|luna>_<low|medium|high|xhigh|max>
ams_spark_<low|medium|high>
ams_daybreak_blue_max
```

The packaged defaults are `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.3-codex-spark`, and the optional account-gated `gpt-daybreak-blue-latest` access lane. Treat them as requested routes, not proof of account availability, entitlement, access-path activation, or observed runtime identity.

## Canonical profile contract

The exact bundled bytes define each managed name, description, model or access lane, reasoning effort, bounded non-root instructions, and Codex V2 guidance overrides. All profiles use the same permission-neutral field shape:

```toml
name = "ams_<profile>"
description = "..."
model = "..."
model_reasoning_effort = "..."
developer_instructions = """..."""

[features.multi_agent_v2]
usage_hint_text = """..."""
subagent_usage_hint_text = """..."""
multi_agent_mode_hint_text = """..."""
```

Managed profiles must not set `sandbox_mode`, approval policy, network access, writable roots, tool grants, provider credentials, authorization claims, or other permission overrides. Permissions and task authority come only from higher-priority platform/user/project policy and the current work order. Spark and Daybreak Blue have no exclusive privilege and remain worker-only.

Every profile preserves these orchestration invariants:

- bounded non-root session; no AMS activation/control access;
- explicit stable work-order ID, root objective, immutable logical parent, role, and matching authority;
- `worker`/`none` is a leaf;
- `delegated-manager`/`request` may request root-mediated descendants but never spawn independently or expand authority;
- Spark and Daybreak Blue accept only `worker`/`none`;
- a Daybreak Blue order additionally requires its operation, stable fallback unit, qualifying refusal, provenance, custody, ownership, allocation, non-secret Trusted Access/data context, route disposition, data-free preflight evidence, authorized purpose, frozen scope/data boundary, route evidence, and one-task-attempt fields from `daybreak-blue.md`;
- scope, permissions, ownership, validation, and Git authority come from the work order;
- only the root communicates with the user and accepts project completion.

For Codex V2 dispatch, use the supported equivalent of `fork_turns = "none"` and supply the compact work order directly. Verify the selected effective profile immediately before spawn and record requested identity. The platform may reread the role at spawn, so observed identity remains evidence rather than a guarantee.

## Requested and observed route evidence

For every profile, exact canonical bytes establish only the requested configuration. Record the requested profile, model, and reasoning effort before dispatch. Record the observed execution identity only when the platform exposes it; otherwise use `observed=unavailable` without claiming verification.

For Daybreak Blue, task data may not be dispatched from profile selection alone. The exact profile must first complete the nonce-bound, data-free `access-preflight` required by `daybreak-blue.md` for the exact access-context ID. A successful preflight proves that Codex accepted the requested custom-agent path and returned a worker-only result through the recorded logical parent; it is not independent attestation of an unobservable effective model. Record `observed=unavailable` when necessary without forcing worker self-attestation. A mismatch, malformed preflight receipt, entitlement or access-path error, wrong access context, or unsupported model/effort closes the route under the recorded disposition and must be reported exactly.

Account or workspace approval is external entitlement, not profile state. Before preflight, the root records the non-secret approved identity/membership basis, organization/workspace/project, Codex product surface, internal-only confirmation, retention requirement/coverage, and provisioning/retention evidence IDs. Do not infer Trusted Access from a bundled file, successful installation, model catalog, prior session, or absence of an error. Do not change credentials, organizations, workspaces, permissions, product surfaces, or retention controls to repair Daybreak automatically.

## Safe profile operations

Require safe containment beneath the chosen registry, regular non-redirected files, bounded stable reads, UTF-8 without BOM/NUL/CR and final LF, case/normalization collision checks, serialized writers, staged replacement, backup, and post-write verification.

`profile_management = "auto"` permits creating a selected **missing** profile from the exact bundled asset after proving the target is absent and unclaimed. It does not permit automatically replacing an existing differing file. `profile_management = "installer"` reports the defect without an automatic write. When a selected profile cannot be used, choose a truthful compatible loaded alternative and record the substitution, or report the exact blocked route; never weaken the profile or loop repair. Daybreak Blue has no compatible ordinary-profile substitution after a qualifying cyber refusal. A failed mandatory preflight or authoritative account, entitlement, context, model/effort, or access-path blocker closes that route and cannot be repaired by retrying unchanged standard routes.

An existing differing profile may be replaced only during a direct user-authorized install/repair and only when the installer proves it is an exact current or explicitly recognized prior official canonical profile. Any customized, marker-only, malformed, ambiguous, or user-authored file is preserved and blocks replacement. The user may review, rename, remove, or manually reconcile it before retrying.

No legacy schema/profile migration logic is active beyond the exact prior public Spark profiles explicitly recognized by the installer for removal of their former sandbox override.
