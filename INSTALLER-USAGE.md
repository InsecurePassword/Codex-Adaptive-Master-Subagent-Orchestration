# Installer Usage

The repository includes two interactive installers:

- `install.ps1` for Windows PowerShell through `powershell.exe`
- `install.sh` for Linux through POSIX `sh`

Both installers show the same menu:

1. Option A — installer skill plus permanent runtime (**recommended**)
2. Option B — one unified skill
3. Option C — lean runtime with external setup and repair
4. Uninstall package-managed Adaptive Master–Subagent Orchestration files

Pressing Enter without a selection chooses Option A.

## Windows

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://raw.githubusercontent.com/InsecurePassword/adaptive-master-subagent-orchestration/refs/heads/main/install.ps1' | iex"
```

## Linux

```sh
curl -fsSL https://raw.githubusercontent.com/InsecurePassword/adaptive-master-subagent-orchestration/refs/heads/main/install.sh | sh
```

## Non-interactive selection

Set `AMS_INSTALL_OPTION` to `A`, `B`, `C`, or `UNINSTALL`.

Windows example:

```powershell
$env:AMS_INSTALL_OPTION='A'; powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

Linux example:

```sh
AMS_INSTALL_OPTION=A sh ./install.sh
```

Optional environment variables:

- `AMS_INTENSITY=auto|minimal|moderate|heavy|extreme`
- `AMS_EXCLUDE_SPARK=1`
- `AMS_SPARK_EFFORTS=low,medium,high`
- `AMS_UNINSTALL_FORCE=1` to confirm non-interactive uninstall
- `CODEX_HOME` to use a non-default Codex state directory

## Uninstall scope

The uninstall option removes only:

- recognized Adaptive Master–Subagent plugin directories and managed backup or staging directories;
- matching personal marketplace entries;
- agent profile files carrying the package-managed marker;
- `$CODEX_HOME/ams-orchestration.toml`;
- recognized legacy user-level skill directories.

It leaves unrelated profiles, unrelated marketplace entries, and project-level `.codex` configuration files unchanged.
