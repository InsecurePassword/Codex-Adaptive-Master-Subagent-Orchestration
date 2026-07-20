# Changelog

## Unreleased

- Added interactive Windows and Linux installers at the repository root.
- Made Option A the default recommended installer choice.
- Added managed uninstall as menu option 4.
- Simplified the root and package READMEs.
- Moved detailed package setup into `MANUAL-INSTALLATION.md`.
- Removed download instructions based on repository visibility.
- Corrected orchestration terminology so `extreme` is consistently the highest intensity.
- Completed a transactional installer audit with command-line selector bypass, strict manifests, safe option switching, bounded process-tree cleanup, rollback tests, offline uninstall, and expanded integration coverage.
- Restricted managed-file ownership to an exact first-line marker so marker text inside user-authored TOML values or profile descriptions is preserved.
- Refused root uninstallers reached through symlinked or non-regular path components.
- Added explicit lock diagnostics and regression coverage for permission errors, malformed locks, symlinks, stale owners, and cleanup after failures.

## 3.1.0

- Reorganized the release into Options A, B, and C.
- Added interrupted-project recovery to each runtime option.
- Added persistent `auto`, `minimal`, `moderate`, `heavy`, and `extreme` intensity modes.
- Preserved 15 Sol/Terra/Luna profiles and 3 optional Spark profiles.
- Added plugin manifests, profile installers, intensity configuration, validation, and package audits.
