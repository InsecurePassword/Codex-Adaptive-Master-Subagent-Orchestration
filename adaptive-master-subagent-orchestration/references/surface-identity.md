# AMS canonical mutable-surface identity

Read completely only when an enabled `task_graph_safeguards` or `shared_worktree_verification` capability requires precise dependency/ownership admission and no authoritative project-native identity rule supersedes it. This reference performs no scan, dispatch, or write.

Normalize ownership to project-relative logical paths. Reject absolute paths, traversal, empty ambiguous owners, and unsupported syntax. Treat case variants, separator variants, Unicode-normalization variants, parent/descendant paths, potentially overlapping globs, and aliases through branch, worktree, artifact, schema, manifest, migration, index, or lock identity as one mutable surface whenever the target platform or project can resolve them together.

When equivalence cannot be disproved, assume overlap and serialize writers or isolate workspaces. This is a scheduling and evidence boundary, not an operating-system sandbox or cryptographic attribution claim.
