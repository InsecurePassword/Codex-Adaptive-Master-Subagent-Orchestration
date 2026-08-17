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

The packaged defaults are `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.3-codex-spark`, and the optional account-gated `gpt-daybreak-blue-latest` lane. Treat them as requested routes, not proof of account availability, entitlement, access-path activation, or observed runtime identity.

## Canonical profile contract

The exact bundled bytes define each managed name, description, requested model/access lane, reasoning effort, bounded non-root instructions, and Codex V2 guidance overrides:

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

Managed profiles must not set `sandbox_mode`, approval policy, network access, writable roots, tool grants, provider credentials, authorization claims, target authority, or other permission overrides. Permissions and task authority come only from higher-priority platform/user/project policy and the current work order.

Every profile preserves:

- bounded non-root operation; no AMS activation or control-surface access;
- explicit stable work-order ID, root objective, immutable logical parent, role, and matching authority;
- `worker`/`none` as a leaf;
- `delegated-manager`/`request` as request-only root-mediated delegation;
- Spark and Daybreak Blue as worker-only;
- work-order ownership, scope, permissions, validation, and Git authority;
- root-only user communication and project acceptance.

A Daybreak order additionally requires the complete operation-specific contract from `daybreak-blue.md`: fallback unit, canonical access-route record and generation, single-flight reservation, normalized provisioned access path/execution surface, signed-in session generation, Trusted Access/data context, proof mode, verification evidence/budget, provenance, custody, ownership/allocation, frozen boundaries, task attempt, and the correct universal `RESULT` plus addendum.

For Codex V2 dispatch, use the supported equivalent of `fork_turns = "none"` and supply the compact work order directly. Verify the selected effective profile immediately before spawn and record requested identity. The platform may reread the role at spawn, so observed identity remains evidence rather than a guarantee.

## Requested, observed, and capability evidence

For every profile, exact canonical bytes establish only requested configuration. Record requested profile, model, and effort before dispatch. Record observed execution identity only when the platform exposes it; otherwise use `observed=unavailable` without claiming verification.

For Daybreak:

- profile selection or installation never authorizes task-data dispatch;
- the root must first create or resolve the canonical route record keyed by the normalized provisioned access path, compatible execution surface, approved identity boundary, retention treatment, exact profile SHA-256/model/effort, and current signed-in Codex session generation;
- the route record is single-flight, shared by every unit with that key, and may reserve only one fallback unit at a time;
- verification is bound to that unit, parent, custody state, intensity shape, objective, and route/session generation and is never reusable across units or sessions; before confirmed task start, interruption, compaction, handoff, root replacement, approval wait, or identity/path uncertainty invalidates it;
- the capability-preflight must use platform-attested identity, the current OpenAI onboarding validation workflow, or a distinguishing non-project defensive fixture with the required same-fixture standard-Sol control refusal;
- a nonce echo proves transport only;
- successful verification returns universal `RESULT` plus `DAYBREAK CAPABILITY PREFLIGHT ADDENDUM`;
- a mismatch, non-distinguishing result, malformed result, entitlement/access failure, incompatible path/surface, unsupported model/effort, uncertain start/result, or exhausted verification/task process-start budget closes the canonical route record as defined in `daybreak-blue.md`.

Account/workspace/API approval is external entitlement, not profile state. Do not infer Trusted Access from bundled bytes, installation, a model catalog, a prior session, or absence of an error. Do not change credentials, organizations, workspaces, API projects, execution surfaces, permissions, or retention controls to repair Daybreak automatically.

## Safe profile operations

Require safe containment beneath the chosen registry, regular non-redirected files, bounded identity-stable reads, UTF-8 without BOM/NUL/CR and final LF, case/normalization collision checks, serialized writers, staged replacement, backup, and post-write verification.

`profile_management = "auto"` permits creating a selected **missing** profile from the exact bundled asset after proving the target is absent and unclaimed. It never replaces an existing differing file. `profile_management = "installer"` reports the defect without an automatic write.

When an ordinary selected profile cannot be used, choose a truthful compatible loaded alternative and record substitution, or report the exact blocked route. Never weaken a profile or loop repair. Daybreak has no compatible ordinary substitution after a qualifying cyber refusal. A closed canonical Daybreak route cannot be bypassed by retrying unchanged standard routes, creating another fallback unit, changing parentage, or probing from another surface.

An existing differing profile may be replaced only during a direct user-authorized install/repair and only when the installer proves it is exact current or explicitly recognized prior official canonical content. Any customized, marker-only, malformed, ambiguous, or user-authored file is preserved and blocks replacement.

No legacy schema/profile migration logic is active beyond the exact prior public Spark profiles explicitly recognized by the installer for removal of their former sandbox override.
