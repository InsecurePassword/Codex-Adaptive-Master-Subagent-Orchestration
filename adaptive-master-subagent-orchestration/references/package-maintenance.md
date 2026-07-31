# AMS package maintenance

Read completely only for explicit install/update/repair/rollback/uninstall, package-integrity suspicion, mixed-generation recovery, or reload-required state. Package maintenance is root-only and exclusive with active dispatch and other AMS control writes.

## Authority and quiescence

Require explicit user authority for package mutation or uninstall. Before mutation, stop new dispatch/control starts, finish or roll back atomic control writes, let safe project work reach useful boundaries, collect evidence, preserve exact resumption state, and close all non-root sessions. Defer mutation when safe closure would lose mandatory work or evidence.

## Identity and trust boundary

Capture the active version and, when observable, the deterministic runtime fingerprint before change. Fingerprint every regular package file recursively beneath the installed root: encode relative paths as UTF-8 with `/`, no leading `./`; sort by ordinal path bytes; append `<lowercase-sha256> <byte-length> <relative-path>\n`; hash the final-LF manifest. `SKILL.md`, `VERSION`, `agents/openai.yaml`, and every packaged reference are mandatory members, not an exhaustive list.

Reject candidate or installed package members that are absolute, escaping, empty/`.`/`..`, invalid UTF-8, non-NFC, control-character-bearing, case/normalization-colliding, linked/redirected, encrypted, unreadable, oversized, unstable, or unexpected. Require regular files, safe bounded reads, UTF-8 without BOM/NUL/CR and final LF for text, exact required membership, parseable frontmatter/YAML, resolvable references, a supported explicit version, and an authorized source/release identity when available. Never invent or silently bump a version.

## Mutation

Serialize package writers with an exclusive lock or equivalent compare-and-swap discipline. Build and validate the complete candidate outside the installed root; keep backup/checkpoint outside it. Prefer an atomic directory swap. If unavailable, apply from a recorded manifest and restore/verify the pre-change checkpoint on any failure. Never leave mixed runtime generations. After commit, validate membership, content, version, and fingerprint again.

If replacement fails, restore and verify the exact prior package. If both replacement and rollback verification fail, mark the package unusable: stop ordinary AMS dispatch/control work and permit only bounded recovery or fail-safe disable with the exact reinstall action reported.

The current session continues under its pre-change contract only for bounded reporting/recovery and must distinguish active from installed version and fingerprint. A behavior-changing install, update, repair, rollback, or uninstall requires Codex reload/restart before normal AMS work.

## Uninstall

Standard uninstall removes only the verified installed AMS package root. Preserve project and global settings, recovery state, generated profiles, and unrelated skills/profiles unless the user explicitly authorizes separate proven cleanup. Refuse redirected or ambiguous roots. Report what remains and require reload.
