# AMS package maintenance

Read completely only for an explicit install, update, repair, rollback, uninstall, package-integrity suspicion, or reload-required state. Package maintenance is root-only and exclusive with active dispatch and other AMS control writes.

## Authority and quiescence

Require direct user authority before package mutation or uninstall. Stop new dispatch, finish or roll back atomic control writes, let safe work reach a useful boundary, collect results, and close non-root sessions before mutation. Preserve continuity through the current root state, an existing authorized project-native record, or a concise user-visible handoff; never create an AMS-specific recovery file.

## Canonical source and validation

The standard installers fetch `install-manifest.txt` and the exact declared files only from the canonical repository `main` tree. They expose no environment-variable override for repository ref, manifest URL, or raw source. A mirror, alternate ref, or other source requires a separate explicit user-requested/manual procedure and is not part of the normal installer.

Validate exact membership, byte lengths, SHA-256 values, version, profile invariants, file safety, and a byte-identical second manifest read before replacement. Never edit `$CODEX_HOME/config.toml` or grant sandbox, approval, network, writable-root, or tool permissions.

## Mutation and repair

Serialize package writers, stage the complete candidate outside the installed root, back up the prior skill and any profile eligible for replacement, and commit transactionally. Restore and verify the prior state on failure. Existing profiles are replaceable only when byte-identical to the current asset or an exact installer-recognized prior official canonical file; otherwise fail closed until the user explicitly reconciles the file.

A behavior-changing install, update, repair, rollback, or uninstall requires Codex reload/restart before normal AMS work.

## Uninstall

Standard uninstall removes only the verified AMS skill directory. Preserve project/global settings, installed profiles, and unrelated files unless the user explicitly authorizes separate proven cleanup. Refuse redirected or ambiguous roots.
