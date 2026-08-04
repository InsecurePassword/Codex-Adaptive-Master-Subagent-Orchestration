# AMS shared-worktree wave control

Read completely only when `shared_worktree_verification = true`, two or more active or potentially live writers share one working tree, attribution must be established, and no authoritative project-native verifier supersedes this capability. The setting never creates a wave. Do not load for serial writers, read-only sessions, or isolated worktrees.

## Preconditions

The root remains scheduler and sole physical spawn authority. Load `surface-identity.md` for this enabled shared-tree wave unless a project-native identity rule supersedes it. Parallel shared-tree work is allowed only when dependencies are ready, ownership scopes are disjoint under that rule, and coordination value exceeds verification burden. A shared tree is not a security sandbox and cannot cryptographically attribute a write.

Record:

```text
Wave ID / Working-tree identity / Pre-wave receipt:
Selected work orders and normalized ownership scopes:
Dependency state / Authorized Git-visible path union:
Authorized non-Git artifacts and receipt method:
Post-wave validation owner:
```

Use a Git tree, commit, complete diff baseline, or equivalent project-native snapshot that distinguishes existing user work from wave changes. Do not use the mutable Git index as AMS task state.

## Scheduling and evidence

Apply `surface-identity.md`; do not redefine its normalization contract here. Serialize cross-cutting surfaces unless one writer owns the complete surface. Every order states exact changed-path reporting. Workers preserve user/concurrent edits and stop on newly discovered overlap.

After every writer reaches a safe boundary or exits:

1. capture one post-wave receipt against the pre-wave receipt;
2. enumerate the complete observed changed-path union;
3. compare each declaration with authorized ownership and evidence;
4. block acceptance for paths outside the authorized union;
5. quarantine unresolved attribution, overlap, or live-writer uncertainty;
6. integrate and validate only after ownership is reconciled.

An empty diff is valid. Additions, deletions, renames, binary changes, and mode changes remain in scope. A cross-owner write leaves both results unaccepted until sequence is reconstructed or work reruns in isolation.

Git-ignored, generated, external, or non-Git artifacts require explicit ownership and a separate bounded receipt such as exact paths plus hashes, a project manifest, or isolated artifact directory. Do not read ignored files broadly merely to improve attribution.

## Failure and cleanup

Preserve violation evidence in an authorized transient or project-native location, keep it out of Git unless required, and remove it when no longer needed. Do not create an AMS task database or recovery ledger. Restore or supersede affected state only through an authorized bounded order with proven ownership.
