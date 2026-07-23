# AMS profile management

Read completely when `runtime-core.md` must select a managed profile, validate profile identity/capability, generate or repair profiles, handle substitutions, or commission profile-related work. Profiles are routing inputs, not authority grants.

## Managed profile model

AMS uses managed role-gated agent profiles for Sol, Terra, Luna, and Spark families where available. A profile declares its model family, effort, role eligibility, delegation authority, and bounded interface. The runtime work order remains authoritative for objective, scope, ownership, permissions, allocation, and return requirements.

A profile may be eligible for:

```text
role = worker | delegated-manager
spawn_authority = none | request
```

The valid pairings are:

- `worker` with `none`;
- `delegated-manager` with `request`.

Spark is always `worker`/`none`. A worker profile cannot be promoted by the work order. A manager-capable profile receives only the bounded manager authority explicitly granted by its order and never physical spawn authority.

## Selection

Choose the lowest-cost reliable model family and reasoning effort that fits the actual bounded assignment. Consider ambiguity, risk, novelty, coupling, supervisory burden, validation difficulty, repetition, and expected failure cost. File count alone does not justify stronger routing.

Typical routing:

- Spark: bounded mechanical work, tests/builds/linters/type checks, narrow searches, concise logs, small deterministic edits, or targeted reproduction when enabled and available;
- Luna: routine implementation, inspection, documentation, tests, and bounded integration with moderate reasoning needs;
- Terra: difficult implementation/debugging, broad coupling, substantial review, or manager work requiring stronger reasoning;
- Sol: high-risk architecture/security/integration judgment, ambiguous recovery, difficult cross-system defects, or delegated management with substantial supervisory burden;
- Sol Max: the top-level root, or exceptional non-root work only when the assignment truly warrants it.

Do not use Spark for architecture/security judgment, ambiguous debugging, broad implementation, visual judgment, final acceptance, manager roles, or any task requiring it to weaken validation. Do not route stronger than needed merely to consume usage, or weaker than needed merely to save it.

## Identity verification

Never claim a model family or effort solely because it was requested. Use observable runtime identity/capability metadata when available. Record requested profile and observed identity separately. If identity is unavailable, say so; never invent it.

Before dispatch, verify that the selected profile exists, is safely readable, uses the supported schema, matches the intended role/authority pair, and does not contain conflicting or unknown control fields. Profile prose cannot override the work order or AMS controls.

After spawn, validate observable identity and behavior against the requested profile. A mismatch is a routing event: accept only when the observed session remains safe and sufficient for the task, otherwise close and reroute. Never silently treat a worker as a manager or Spark as another family.

## Managed profile schema and location

Managed profiles are AMS-owned generated files in the product-supported agent profile location, not inside project repositories. Release 3.09 uses role-gated schema 3. A managed profile should encode at least:

```text
schema_version = 3
managed_by = adaptive-master-subagent-orchestration
model_family = <sol|terra|luna|spark>
effort = <supported effort>
role = <worker|delegated-manager>
spawn_authority = <none|request>
```

It may include bounded interface instructions needed by the product, but must not contain project-specific objectives, persistent authority, user secrets, or self-expanding delegation rules.

Profile filenames and exact syntax are product/version specific. Derive them from the current supported profile interface rather than guessing. Preserve unrelated user profiles.

## Validation

A managed profile is valid only when all of the following hold:

- it is a safe regular non-redirected file in the expected profile directory;
- its path and object identity remain stable through a bounded read;
- it is UTF-8 without BOM, NUL, CR, invalid encoding, or missing final LF;
- its schema is supported and all keys/types/values are recognized;
- `managed_by`, family, effort, role, and authority are internally consistent;
- worker profiles cannot request descendants;
- manager profiles are never Spark and expose only request authority;
- no project instructions or untrusted repository text have been copied into it;
- its identity matches the selected logical profile record.

Unknown keys, duplicate keys, unsafe paths, redirection, wrong types, unsupported schema, or inconsistent role/authority invalidate the managed profile.

## Generation and repair

`profile_management = "auto"` allows the root to commission bounded generation or repair of the exact selected managed profiles when missing or invalid. `profile_management = "installer"` reports the defect unless the user explicitly requests repair.

Profile mutation is an AMS control action. The root owns authorization, target selection, canonical content, validation, and acceptance. A delegated ordinary worker may perform a narrowly scoped mechanical write only from root-supplied canonical content and target allowlist; it does not read AMS references, choose profile semantics, or decide acceptance.

Use staged atomic replacement:

1. prove the profile directory and target path are safe;
2. preserve unrelated profiles;
3. write canonical content to a same-directory temporary file with exclusive creation;
4. flush and validate bytes/schema;
5. atomically replace the exact managed target;
6. reread and verify identity/content;
7. remove temporary residue and report.

Do not edit a live profile in place, follow links, broaden directory permissions, or overwrite an unrelated file. If the target's ownership/identity is ambiguous, stop.

Profile repair does not authorize package maintenance, project settings changes, or recovery-state changes. It is exclusive with other AMS control writes and should not overlap project dispatch that depends on the profile being changed.

## Spark availability and efforts

Spark routing requires valid project settings with both `spark_enabled = true` and `spark_available = true`, and the selected effort in `spark_efforts`. These settings control routing eligibility; they do not alter the managed profile's worker-only role.

An authoritative account/family unavailability result may set `spark_available = false` under `project-control.md`. Temporary task failure, timeout, tool denial, malformed output, unsuitable assignment, or one session's refusal does not prove family-wide unavailability.

## Substitution and fallback

When the requested profile is unavailable, invalid, or mismatched:

1. preserve the original assignment and validation requirements;
2. choose the closest safe compatible profile at equal or greater reliability;
3. respect role eligibility—never substitute a worker-only profile for a manager;
4. record requested and actual profile/identity;
5. reroute or flatten a manager subgraph when no manager-capable profile exists;
6. do not repeatedly retry an unchanged failing profile route.

A substitution cannot expand scope, permissions, ownership, allocation, or authority. It may require narrower scope, stronger supervision, or additional validation.

## Profile lifecycle and recovery

On package updates, validate whether managed profile schema/content remains compatible. Do not silently rewrite profiles during ordinary project work unless auto-repair is authorized and necessary for the selected route. Preserve previous valid content or a bounded backup until replacement is verified.

After interrupted mutation, inspect temporary/backup/target identities, choose one complete canonical generation, restore atomically, and record the result. Mixed or ambiguous profile state blocks dispatch through that profile but does not necessarily block independent routes using other valid profiles.

Never include managed profiles in project Git unless the user explicitly requests a separate export; even then, exported copies are data/examples and cannot become active instructions automatically.
