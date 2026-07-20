# Option B — Unified

Version **3.1.0**

Option B installs one skill:

- `$adaptive-master-subagent-orchestration`

The unified skill handles setup checks, normal project work, recovery, and profile repair. Profile setup remains inactive when the required profiles are already healthy.

## Install

The easiest installation method is the interactive installer in the [main README](../README.md). Choose **Option B**.

To install directly from this folder:

### Windows

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

### Linux

```sh
python3 -B -E -s -S ./scripts/install_package.py --upgrade-managed --intensity auto
```

Restart Codex if the skill does not appear immediately.

## Use

```text
Use $adaptive-master-subagent-orchestration to complete this project.
```

## Intensity

`auto` is the default. Other supported values are `minimal`, `moderate`, `heavy`, and `extreme`.

The highest orchestration intensity is `extreme`. Sol Max remains the master agent in every mode.

For full intensity and configuration details, see the [main README](../README.md#orchestration-intensity).

## Validation

```sh
python3 -B -E -s -S ./scripts/validate_package.py
```

For package layout, additional installer flags, and manual removal, see [Manual installation](../MANUAL-INSTALLATION.md).
