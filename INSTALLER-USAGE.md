# Installer Usage

The repository includes two root installers:

- `install.ps1` for Windows PowerShell
- `install.sh` for Linux and other POSIX-compatible systems

Running either installer without an option shows a menu. Pressing **Enter** selects **Option A**, the recommended package.

## Direct installation

### Windows

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://raw.githubusercontent.com/InsecurePassword/adaptive-master-subagent-orchestration/refs/heads/main/install.ps1' | iex"
```

### Linux

```sh
curl -fsSL https://raw.githubusercontent.com/InsecurePassword/adaptive-master-subagent-orchestration/refs/heads/main/install.sh | sh
```

## Bypass the menu

### Windows

```powershell
# Option A — recommended
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Option A

# Option B — unified skill
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Option B

# Option C — lean runtime
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Option C

# Uninstall
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Option Uninstall -Force
```

`-InstallOption` is an alias for `-Option`.

### Linux

```sh
# Named option
sh ./install.sh --option A

# Positional option
sh ./install.sh B

# Lean runtime without Spark
sh ./install.sh --option C --exclude-spark

# Uninstall
sh ./install.sh --option UNINSTALL --force
```

Values `1`, `2`, `3`, and `4` may be used in place of `A`, `B`, `C`, and `UNINSTALL`.

## Common settings

| Setting | PowerShell | Linux | Environment variable |
|---|---|---|---|
| Installation option | `-Option A` | `--option A` | `AMS_INSTALL_OPTION=A` |
| Installation home | `-HomeDirectory C:\Users\name` | `--home /home/name` | `AMS_HOME` |
| Initial intensity | `-Intensity heavy` | `--intensity heavy` | `AMS_INTENSITY` |
| Spark profiles | `-SparkEfforts low,medium` | `--spark-efforts low,medium` | `AMS_SPARK_EFFORTS` |
| Exclude Spark | `-ExcludeSpark` | `--exclude-spark` | `AMS_EXCLUDE_SPARK=1` |
| Confirm uninstall | `-Force` | `--force` | `AMS_UNINSTALL_FORCE=1` |
| Local repository ZIP | `-ArchivePath .\repo.zip` | `--archive-path ./repo.zip` | `AMS_ARCHIVE_PATH` |
| Repository ref | `-RepositoryRef main` | `--ref main` | `AMS_REF` |

`CODEX_HOME` may be set separately when Codex data should be stored outside the default `.codex` directory.

## Offline installation

Download or create a ZIP of the repository, then pass it directly to the root installer:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Option A -ArchivePath .\adaptive-master-subagent-orchestration.zip
```

```sh
sh ./install.sh --option A --archive-path ./adaptive-master-subagent-orchestration.zip
```

The archive is validated before extraction. Unsafe paths, links, duplicate entries, missing package files, extra unlisted package files, and checksum mismatches are rejected.

## Updates and package switching

Running the installer again updates the selected package. Selecting a different option replaces the previous Adaptive Master–Subagent package instead of leaving multiple active options installed.

Package-managed files are backed up before replacement. Unrelated plugins, profiles, marketplace entries, and project-level configuration files are preserved.

## Uninstall scope

Uninstall removes only recognized package-managed data:

- Adaptive Master–Subagent plugin directories and managed staging or backup directories
- matching marketplace entries
- agent profiles carrying the package-managed marker
- the user-level `ams-orchestration.toml`
- recognized legacy user-level skill directories

Unrelated files and project-level `.codex` configuration remain unchanged.

## Verify the installers

Run the complete offline audit from the repository root:

```sh
python3 -B -E -s -S ./scripts/audit_installers.py
```

The audit checks shell and Python syntax, PowerShell syntax when a PowerShell runtime is available, root installer integration, every package installer, rollback, locking, option switching, archive validation, uninstall, and package manifests.
