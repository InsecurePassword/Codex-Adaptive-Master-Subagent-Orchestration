# Remote Installer Usage

The repository includes two interactive remote installers at its root:

- `install.ps1` for Windows PowerShell 5.1 through `powershell.exe`
- `install.sh` for Linux through POSIX `sh`

Both installers present the same menu:

1. Option A — installer skill plus permanent runtime (**recommended**)
2. Option B — unified skill with conditional bootstrap
3. Option C — lean runtime with mandatory deterministic installation
4. Uninstall package-managed Adaptive Master–Subagent Orchestration files

Pressing Enter without a selection chooses Option A.

## Windows

When the repository is public:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://raw.githubusercontent.com/InsecurePassword/adaptive-master-subagent-orchestration/refs/heads/main/install.ps1' | iex"
```

While the repository is private, set `GITHUB_TOKEN` to a fine-grained token with read access to the repository, then run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$h=@{Authorization='Bearer ' + $env:GITHUB_TOKEN;Accept='application/vnd.github.raw+json';'X-GitHub-Api-Version'='2022-11-28'}; iex (irm -Headers $h 'https://api.github.com/repos/InsecurePassword/adaptive-master-subagent-orchestration/contents/install.ps1?ref=main')"
```

## Linux

When the repository is public:

```sh
curl -fsSL https://raw.githubusercontent.com/InsecurePassword/adaptive-master-subagent-orchestration/refs/heads/main/install.sh | sh
```

While the repository is private, export `GITHUB_TOKEN` with repository read access, then run:

```sh
curl -fsSL \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.raw+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/InsecurePassword/adaptive-master-subagent-orchestration/contents/install.sh?ref=main" | sh
```

## Non-interactive selection

The scripts normally prompt for a selection. Automation can set `AMS_INSTALL_OPTION` to `A`, `B`, `C`, or `UNINSTALL`.

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
- `AMS_UNINSTALL_FORCE=1` for confirmed non-interactive uninstall
- `CODEX_HOME` to override the default Codex state directory
- `GITHUB_TOKEN` while the repository remains private

## Uninstall scope

The uninstall option removes only:

- recognized Adaptive Master–Subagent plugin directories and their managed backups/staging directories;
- matching personal marketplace entries;
- agent profile files carrying the package managed marker;
- `$CODEX_HOME/ams-orchestration.toml`;
- recognized legacy user-level skill directories.

It preserves unrelated profiles, unrelated marketplace entries, and project-local `.codex` configuration files.
