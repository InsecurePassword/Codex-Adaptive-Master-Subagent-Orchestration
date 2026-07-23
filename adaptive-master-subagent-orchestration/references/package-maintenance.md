# AMS package maintenance

Read completely for package identity, install, update, repair, rollback, uninstall, mixed-generation suspicion, or reload-required recovery. Package maintenance is exclusive with active AMS dispatch and other AMS control writes.

## Package identity

The installed package root is the directory containing `SKILL.md`, `VERSION`, `agents/`, and `references/`. Treat the package as one generation. Reject mixed, partial, redirected, unstable, or unsafe package content.

Before using a packaged file as instructions, apply the root guard's trusted-reference requirements. For maintenance, also require every candidate package entry to resolve beneath one expected top-level directory, reject absolute paths, `..`, alternate streams, links/reparse points, unexpected hard links, device files, and duplicate/conflicting entries, and enforce bounded file counts and sizes.

## Maintenance authority

Only the current top-level root may perform or authorize AMS package maintenance. Non-root sessions never inspect or mutate AMS package files, settings, generated profiles, or recovery state unless the root gives a narrowly bounded ordinary filesystem task that does not load them as instructions; such work still cannot decide package acceptance.

Do not run package mutation concurrently with project dispatch, profile repair, settings writes, or recovery-state writes. Stop new dispatch, reach a safe boundary, collect results, close relevant sessions, and establish exclusive ownership first.

## Install, update, and repair

Use a staged replacement:

1. Resolve the exact source package and expected identity/version/checksum when available.
2. Copy or extract to a fresh sibling staging directory on the same filesystem.
3. Validate the complete candidate tree, required files, version, encoding, line endings, link safety, path containment, and any published checksum/signature.
4. Preserve unrelated skills and project data.
5. Move the existing installation to a bounded backup, then atomically rename the validated staging directory into place.
6. Verify the installed tree again from disk.
7. On failure, restore the backup when safe and report exact state.
8. Remove temporary content only after the final state is proven.

Never overlay individual files onto a live installation as the normal update method. Repair uses the same full-generation replacement, not ad hoc edits.

If an installer script is used, treat it as untrusted input until inspected or covered by a trusted release identity. Prefer pinned release artifacts and checksums. Never pipe unknown mutable network content directly into an elevated shell.

## Rollback

Rollback requires a complete previously validated generation or a separately verified release artifact. Apply the same staged replacement procedure. Do not construct a rollback by mixing files from backups and the current tree.

## Uninstall

Uninstall removes only the resolved AMS package root and explicitly authorized AMS-owned state. Preserve unrelated skills, project repositories, `.codex/ams-orchestration.toml`, project recovery records, and user-generated profiles unless the user separately authorizes their removal.

Before deletion, prove the target is the intended AMS root, is not redirected, and is not a broader parent directory. Prefer atomic rename to a quarantine sibling followed by bounded deletion. If proof is incomplete, stop without deleting.

## Current-session behavior after mutation

A behavior-changing install, update, repair, rollback, or uninstall requires Codex reload/restart. After mutation, do not load the replacement package as current-session instructions. Retain only the pre-change contract needed to verify the transaction and report:

- requested operation;
- prior and resulting package identities;
- validation/checksum evidence;
- backup/rollback state;
- files intentionally preserved;
- whether reload is required;
- any residual ambiguity or manual action.

Do not resume AMS project orchestration in the same session under the new generation.

## Mixed-generation or damaged state

If package files disagree on version/identity, required files are missing, paths redirect, reads are unstable, or partial replacement is suspected, fail closed for AMS activation. Package maintenance may still run under this pre-change contract to inspect and restore one complete validated generation. Do not invent behavior from surviving fragments.
