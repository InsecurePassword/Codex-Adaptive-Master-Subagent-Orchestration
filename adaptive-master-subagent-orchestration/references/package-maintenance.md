# AMS package maintenance

Read completely only for an explicit install, update, repair, rollback, uninstall, downgrade preparation, runtime-state export/import, or package-integrity request. Package completion does not load this reference by itself. Package maintenance is root-only and exclusive with other AMS package/control writes.

## Authority and shared runtime lock

Require direct user authority before mutation or uninstall. Acquire the shared package/runtime lock defined by `convergence-control.md` before reading or replacing package-local runtime state, and hold it from pre-snapshot through backup deletion or rollback completion. Finish or roll back active control writes first. Do not stop unrelated project sessions solely for package work.

Preserve continuity through current root state, authorized project-native records, a concise handoff, and authorized convergence tracking/history. Convergence records are the sole exception to the prohibition on AMS-specific durable runtime files; create no task database, general recovery ledger, review ledger, settings history, or memory file.

## Canonical source and validation

Standard installers fetch `install-manifest.txt` and exact declared files only from canonical published `main`. Alternate sources require a separate explicit manual procedure.

Validate exact manifest membership, lengths, SHA-256 values, version, profile invariants, file safety, and a byte-identical second manifest read. Package integrity excludes the safe `.runtime` convergence directory because it is runtime state, not release content. Never edit `$CODEX_HOME/config.toml` or grant sandbox, approval, network, writable-root, or tool permissions.

## Mutation, repair, and rollback

Stage the complete candidate outside the installed root. Under the shared lock, validate and snapshot the exact safe runtime layout, back up the prior skill and replaceable profiles, install transactionally, restore runtime state, and compare the preserved snapshot before deleting the backup. Restore and verify prior state on failure.

Existing profiles are replaceable only when byte-identical to the current asset or an exact installer-recognized prior official file. Any other differing profile blocks replacement until explicitly reconciled.

After success, resume ordinary AMS operation. Do not automatically compare prior/current packages, re-audit, reactivate, pause project work, or request user action solely because mutation occurred. Integrity verification occurs only on direct request.

## Downgrade export and import

An older installer may not understand AMS 4.0 package-local convergence state. A supported downgrade therefore requires explicit export before running the older installer:

1. acquire the shared package/runtime lock;
2. validate the exact `.runtime/convergence` layout;
3. copy it to a user-selected directory outside the skill root, preferably beneath `$CODEX_HOME/ams-runtime-export/<UTC-id>/`;
4. record byte lengths and SHA-256 values;
5. release the lock, then run the authorized older installer.

Do not claim the older release can resume those records. Reimport only after reinstalling a compatible AMS version, under its shared lock, after validating every exported path and proving no conflicting active state exists. A direct downgrade without export may destroy convergence state and must be reported before execution.

## Uninstall

Standard uninstall removes manifest-managed package files only within the user-authorized scope. Preserve project/global configuration and installed profiles under existing AMS policy. Before removing the skill root, either preserve safe package-local convergence state in place when the uninstall method supports it or export it using the procedure above. Remove convergence history only with explicit full-runtime-cleanup authority. Refuse redirected or ambiguous roots.
