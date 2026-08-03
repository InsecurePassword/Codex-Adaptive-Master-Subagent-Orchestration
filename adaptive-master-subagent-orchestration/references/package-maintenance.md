# AMS package maintenance

Read only for an explicit install, update, repair, rollback, uninstall, or package-integrity request. Do not load this reference merely because package files changed.

## Authority

Require direct user authority before package mutation or uninstall. Prevent concurrent package writes and pause active dispatch only as needed for the mutation. Preserve project state and never create an AMS-specific recovery file.

## Install, update, repair, and rollback

The standard installers read the canonical repository `main` manifest and declared files. During the requested mutation, they verify the download set, version, file lengths and hashes, profile provenance, and transactional replacement. They never edit `$CODEX_HOME/config.toml` or grant sandbox, approval, network, writable-root, or tool permissions.

Stage the complete candidate, back up replaceable files, commit transactionally, and restore the prior state on failure. Replace an existing profile only when it is byte-identical to the current asset or an exact installer-recognized prior official file; otherwise preserve it and report the conflict.

After a successful install, update, repair, or rollback, resume ordinary AMS operation. Perform no follow-up package check unless the user explicitly requests one.

## Uninstall

Standard uninstall removes only the verified AMS skill directory. Preserve project/global settings, installed profiles, and unrelated files unless the user explicitly authorizes separate proven cleanup.
