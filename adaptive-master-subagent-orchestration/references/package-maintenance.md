# AMS package maintenance

Read completely only for an explicit install, update, repair, rollback, uninstall, or package-integrity request. A package change or completed update does not load this reference by itself. Package maintenance is root-only and exclusive with other AMS package/control writes.

## Authority

Require direct user authority before package mutation or uninstall. Serialize package writers and finish or roll back any active AMS control write before mutation. Do not stop or close unrelated project sessions solely because an install, update, repair, or rollback is running. Preserve continuity through the current root state, an existing authorized project-native record, or a concise user-visible handoff; never create an AMS-specific recovery file.

## Canonical source and validation

The standard installers fetch `install-manifest.txt` and the exact declared files only from the canonical repository `main` tree. They expose no environment-variable override for repository ref, manifest URL, or raw source. A mirror, alternate ref, or other source requires a separate explicit user-requested/manual procedure and is not part of the normal installer.

Validate exact membership, byte lengths, SHA-256 values, version, profile invariants, file safety, and a byte-identical second manifest read before replacement. Never edit `$CODEX_HOME/config.toml` or grant sandbox, approval, network, writable-root, or tool permissions.

## Mutation and repair

Serialize package writers, stage the complete candidate outside the installed root, back up the prior skill and any profile eligible for replacement, and commit transactionally. Restore and verify the prior state on failure. Existing profiles are replaceable only when byte-identical to the current asset or an exact installer-recognized prior official canonical file; otherwise fail closed until the user explicitly reconciles the file.

After a successful install, update, repair, or rollback, resume ordinary AMS operation. A successful install or update does not invoke the `project-control.md` package-transition steering or recovery procedure. Do not compare prior and current package state, compute post-update hashes, re-verify, re-audit, reactivate, pause project work, or request user action solely because the mutation occurred. Package-integrity verification occurs only on direct user request.

## Uninstall

Standard uninstall removes only the verified AMS skill directory. Preserve project/global settings, installed profiles, and unrelated files unless the user explicitly authorizes separate proven cleanup. Refuse redirected or ambiguous roots.
