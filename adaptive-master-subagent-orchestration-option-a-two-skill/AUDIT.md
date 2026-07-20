# Final Package Audit — Adaptive Master–Subagent Orchestration 3.1.0

## Scope

This audit reviewed the three package options, all Markdown documentation, runtime skill definitions, profile installers, manifests, and validation scripts.

## Package structure

- **Option A:** two skills — `$ams-installer` and `$ams-orchestration`.
- **Option B:** one skill — `$adaptive-master-subagent-orchestration`.
- **Option C:** one lean runtime skill — `$ams-orchestration`; profile installation is required.

Recovery is included in every runtime option. Direct subagents cannot create additional agents.

## Orchestration rules

- Sol Max remains the master agent and owns task assignment, model routing, file ownership, integration, validation, and final completion.
- `auto` remains the default intensity.
- Supported intensity values are `auto`, `minimal`, `moderate`, `heavy`, and `extreme`.
- `extreme` is the highest orchestration intensity.
- Sol, Terra, and Luna provide Low through Max profiles. Spark provides Low, Medium, and High profiles only.
- Spark is not used for architecture, security decisions, visual work, or final acceptance.

## Documentation findings

- The root README now leads with the interactive Windows and Linux installers.
- Detailed folder trees and direct package commands are kept in `MANUAL-INSTALLATION.md`.
- Automation and uninstall details are kept in `INSTALLER-USAGE.md`.
- Package READMEs are short and specific to their own option.
- Download instructions no longer depend on repository visibility labels.
- Terminology consistently identifies `extreme` as the highest orchestration intensity.

## Validation

Each package includes `scripts/validate_package.py` and `MANIFEST.sha256`. Validation covers plugin structure, skill metadata, profile TOML, package membership, checksums, installer behavior, intensity configuration, recovery requirements, and option-specific setup rules.

The package manifest must be regenerated whenever a packaged file changes.
