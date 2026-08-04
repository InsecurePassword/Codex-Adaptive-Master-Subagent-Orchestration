# AMS task-graph safeguards

Read completely only when `task_graph_safeguards = true`, dependency admission or mutable-surface ownership is being decided, and no authoritative project-native graph mechanism supersedes it. The setting does not create tasks or scan the repository.

Before dispatch reject self-dependencies, missing mandatory dependency identities, direct or transitive cycles, readiness claims with unaccepted prerequisites, and replacements that silently rewrite historical lineage. A cycle is a planning deviation, not ordinary blocked work; correct, supersede, or split the graph first.

When mutable-surface ownership must be admitted, load and apply `surface-identity.md`; do not define a second normalization contract. When aliasing cannot be resolved safely, serialize writers or use isolated workspaces. These checks protect scheduling and attribution; they are not an operating-system sandbox.
