# Option C — Lean Runtime

Version **3.1.0**

Option C installs one skill:

- `$ams-orchestration`

This package keeps setup and repair logic out of the runtime skill. The external installer must create and maintain the required profiles.

## Install

The easiest installation method is the interactive installer in the [main README](../README.md). Choose **Option C**.

To install directly from this folder:

### Windows

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install-Package.ps1 -UpgradeManaged -Intensity auto
```

### Linux

```sh
python3 ./scripts/install_package.py --upgrade-managed --intensity auto
```

Option C does not allow profile installation to be skipped. Restart Codex if the skill does not appear immediately.

## Use

```text
Use $ams-orchestration to complete this project.
```

## Intensity

`auto` is the default. Other supported values are `minimal`, `moderate`, `heavy`, and `extreme`.

The highest orchestration intensity is `extreme`. Sol Max remains the master agent in every mode.

For full intensity and configuration details, see the [main README](../README.md#orchestration-intensity).

## Validation

```sh
python3 ./scripts/validate_package.py
```

For package layout, additional installer flags, and manual removal, see [Manual installation](../MANUAL-INSTALLATION.md).
