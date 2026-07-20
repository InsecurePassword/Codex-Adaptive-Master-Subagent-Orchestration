# Option A — Recommended

Version **3.1.0**

Option A installs two skills:

- `$ams-installer` for profile setup, checks, repair, and upgrades
- `$ams-orchestration` for normal project work and recovery

This is the recommended option for most users because installation tasks stay separate from the smaller runtime skill.

## Install

The easiest installation method is the interactive installer in the [main README](../README.md). Choose **Option A** or press Enter.

To install directly from this folder:

### Windows

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

### Linux

```sh
python3 ./scripts/install_package.py --upgrade-managed --intensity auto
```

Restart Codex if the skills do not appear immediately.

## Use

For normal projects:

```text
Use $ams-orchestration to complete this project.
```

Use `$ams-installer` only when you need to check, repair, or upgrade the managed profiles.

## Intensity

`auto` is the default. Other supported values are `minimal`, `moderate`, `heavy`, and `extreme`.

The highest orchestration intensity is `extreme`. Sol Max remains the master agent in every mode.

For full intensity and configuration details, see the [main README](../README.md#orchestration-intensity).

## Validation

```sh
python3 ./scripts/validate_package.py
```

For package layout, additional installer flags, and manual removal, see [Manual installation](../MANUAL-INSTALLATION.md).
