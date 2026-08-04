# AMS runtime observation

Read completely only when `runtime_observation = true` or explicitly overridden for this objective, observed role/model/effort/sandbox evidence is required or conflicts, and no authoritative project-native observer supersedes it. The setting alone inspects nothing. Requested routing remains requested; unavailable fields remain `unobservable`.

## Evidence order

1. Inspect public spawn/details metadata first.
2. Record only directly exposed session/parent identity, role/profile, model, effort, sandbox policy type, permission profile type, and working-directory/worktree identity.
3. Compare observed role/model/effort with the selected AMS profile.
4. If required fields are omitted or evidence conflicts, use local rollout corroboration only through a separately installed compatible `ams-runtime-observation` companion.
5. Require public and local evidence to agree when both exist.

Never infer observed identity from a profile name, title, prompt, display label, configuration file, or expected route. Local metadata is corroboration, not cryptographic attestation.

## Companion gate and path safety

Require skill name `ams-runtime-observation` and compatibility marker `4.0`. Report enabled, available, and compatible separately. Resolve the active companion's installed root from the actual companion `SKILL.md`; construct an absolute helper path beneath that root, verify it is a regular non-redirected file, and execute only that path. Never execute a project-relative `tools/` path or an arbitrary same-named script.

Missing/incompatible companion leaves best-effort fields unobservable and blocks only a boundary explicitly requiring local observation. Do not add Python or PowerShell as core AMS prerequisites.

## Acceptance

- Best effort records available fields and leaves omissions `unobservable`.
- Required observation blocks only the affected dispatch, review, or acceptance boundary.
- An observed mismatch is a routing deviation; stop acceptance and reroute/correct rather than relabeling.
- Observation never grants permissions, changes routing, or authorizes inspection beyond the companion allowlist.
