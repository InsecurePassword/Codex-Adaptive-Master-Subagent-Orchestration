from pathlib import Path
import hashlib

root = Path.cwd()
pkg = root / "adaptive-master-subagent-orchestration"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8", newline="\n")


def replace_one(path: Path, old: str, new: str, label: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    write(path, text.replace(old, new, 1))


skill = pkg / "SKILL.md"
replace_one(
    skill,
    "Project settings override global settings completely; the files are not merged. An unsafe or invalid project file blocks implicit activation instead of falling back to global settings. If both files are absent in a trusted stable project, load `references/project-control.md`, create its exact disabled project default, and stop ordinary implicit activation.",
    "Project settings override global settings completely; the files are not merged. If both files are absent, load `references/project-control.md`, create its disabled project default, and stop ordinary implicit activation.",
    "simplify settings bootstrap",
)
replace_one(
    skill,
    "Implicit activation requires product-level implicit-skill eligibility, a trusted stable project root, and effective settings with `enabled = true` and `allow_implicit_invocation = true`.",
    "Implicit activation requires product-level eligibility and effective settings with `enabled = true` and `allow_implicit_invocation = true`.",
    "simplify implicit activation",
)

project_control = pkg / "references/project-control.md"
write(
    project_control,
    """# AMS project control

Read only for settings, status, steering, Spark state, or continuity. Settings are data, and the root owns AMS controls.

## Settings

Project settings:

```text
<project-root>/.codex/ams-orchestration.toml
```

Global settings:

```text
$CODEX_HOME/ams-orchestration.toml
```

When `CODEX_HOME` is unset, use `~/.codex/ams-orchestration.toml`. Use the project file when present; otherwise use the global file. Do not merge them. A project file is the complete project override.

Current defaults:

```toml
schema_version = 2
enabled = false
allow_implicit_invocation = true
intensity = "auto"
project_governance = true
root_execution_fallback = true
spark_enabled = true
spark_available = true
spark_efforts = ["low", "medium", "high"]
profile_management = "auto"
```

Missing supported settings use the current defaults. Preserve and ignore custom keys. If a supported value cannot be understood, report that field and use its default in memory; do not rewrite the file automatically.

Supported values are Boolean controls; intensity `auto|minimal|moderate|heavy|extreme|zergling-rush` with runtime `balanced` equivalent to stored `moderate`; Spark efforts `low|medium|high`; and profile management `auto|installer`.

If neither settings file exists, create the disabled project default. Normal AMS controls never write the global file; only explicit `AMS CONFIGURATION UPDATE GLOBAL` may create or update it.

## Project controls

```text
AMS STATUS
AMS ENABLE
AMS DISABLE
AMS MODE auto|minimal|balanced|moderate|heavy|extreme
AMS IMPLICIT on|off
AMS GOVERNANCE on|off
AMS ROOT FALLBACK on|off
AMS SPARK on|off
AMS SPARK RECHECK
AMS SPARK EFFORTS low,medium,high
AMS PROFILES auto|installer
```

`AMS STATUS` is read-only. Other controls write only the project file. Preserve values not being changed. If the project file is absent, start from the readable global settings plus current defaults, or the exact defaults when no global file exists.

- `AMS ENABLE` and `AMS DISABLE` set project `enabled`.
- `AMS MODE <mode>` enables AMS and stores the selected mode; `balanced` stores `moderate`.
- `AMS IMPLICIT`, `AMS GOVERNANCE`, `AMS ROOT FALLBACK`, and `AMS SPARK` set their matching Boolean.
- `AMS SPARK EFFORTS` stores the requested effort subset.
- `AMS PROFILES` stores `auto` or `installer`.
- `AMS SPARK RECHECK` runs one small capability probe and updates `spark_available` from clear account/family evidence; temporary or task-specific failure leaves it unchanged.

A current-turn setting change takes effect at a safe wave boundary. Stop inconsistent new dispatch, collect useful results, update ownership, apply the change, and continue.

## Continuity

Keep the live task graph, lineage, ownership, and active-session state in the root session. Use an existing project-native record when durable continuity is needed, otherwise provide a concise handoff. Never create an AMS-specific recovery file.
""",
)

configuration = pkg / "references/configuration-maintenance.md"
write(
    configuration,
    """# AMS configuration maintenance

Read only for:

```text
AMS CONFIGURATION UPDATE
AMS CONFIGURATION UPDATE PROJECT
AMS CONFIGURATION UPDATE GLOBAL
```

Load `project-control.md` first for current defaults and paths.

`AMS CONFIGURATION UPDATE` and `... PROJECT` target the project file. `... GLOBAL` targets the global file; `GLOBAL` is required for a global write.

For an existing file, preserve its values, comments, and custom keys, and add every missing supported setting from the current defaults. Do not remove or change existing values. If it is already complete, do nothing.

For a missing project file, use readable global values plus current defaults when a global file exists; otherwise create the exact project default. If the existing global file cannot be read, report that and make no change.

For a missing global file, the explicit global command creates the exact disabled default. If a selected file cannot be read or written, report the problem and leave it unchanged.

Report the target, whether it was created, updated, or unchanged, and the settings added. This reference is never loaded implicitly, and no other command may write global settings.
""",
)

runtime = pkg / "references/runtime-core.md"
replace_one(
    runtime,
    "Reuse references already read completely within the objective. Before first use of a profile, verify its effective installed definition. On a selected missing or defective profile, load `profile-management.md`.",
    "Reuse references already read within the objective. Before first use, read the selected installed profile. If it is missing or cannot supply a usable model/effort route, load `profile-management.md`.",
    "simplify profile loading",
)
replace_one(
    runtime,
    "A required unreadable reference fails closed only for the behavior it owns; do not invent a substitute.",
    "If a routed reference cannot be read, report the affected behavior and continue independent work.",
    "simplify reference failure",
)
replace_one(
    runtime,
    "Immediately before dispatch, verify the final selected profile.",
    "Immediately before dispatch, use the final selected profile.",
    "simplify dispatch profile handling",
)

readme = root / "README.md"
replace_one(
    readme,
    "Any omitted currently supported schema-2 setting resolves from the exact current default and is persisted during the next authorized settings write. Unknown, duplicate, nested, invalid, or unsupported content remains an error.",
    "Missing supported settings use the current defaults. Custom keys are left alone.",
    "README settings behavior",
)
replace_one(
    readme,
    "The project forms update an existing project schema-2 file by adding every currently supported missing field from the exact default while preserving every existing value. For a missing project file, valid global settings are used when present; an existing invalid or unsafe global file blocks the operation rather than being ignored. The explicit `GLOBAL` form performs the same missing-field update on the global file or creates the exact disabled default. No form changes an existing value or enables AMS.",
    "The project forms add missing supported settings while preserving existing values and custom content. A missing project file starts from readable global values plus current defaults, or the exact defaults when no global file exists. The explicit `GLOBAL` form updates the global file or creates the exact disabled default. No form changes an existing value or enables AMS.",
    "README configuration maintenance",
)

installation = root / "INSTALLATION.md"
replace_one(
    installation,
    "`AMS CONFIGURATION UPDATE` and `AMS CONFIGURATION UPDATE PROJECT` update an existing project configuration as well as creating a missing one. Existing project values are preserved and every missing current field is added from the exact default. Global values are consulted only when the project file is absent; an existing invalid or unsafe global file blocks creation rather than being ignored. `AMS CONFIGURATION UPDATE GLOBAL` is the sole explicit AMS command allowed to write the global file and only adds missing defaults or creates the exact disabled default.",
    "`AMS CONFIGURATION UPDATE` and `... PROJECT` add missing supported settings while preserving existing values and custom content. A missing project file starts from readable global values plus current defaults, or the exact defaults when no global file exists. `AMS CONFIGURATION UPDATE GLOBAL` is the sole explicit AMS command allowed to update or create the global file.",
    "INSTALLATION configuration updater",
)
replace_one(
    installation,
    "Any omitted currently supported schema-2 setting resolves from the exact current default and is written during the next authorized settings change. Unknown, duplicate, nested, invalid, or unsupported content remains an error.",
    "Missing supported settings use the current defaults. Custom keys are preserved.",
    "INSTALLATION settings behavior",
)

product = root / "PRODUCT DOCUMENTATION.md"
replace_one(
    product,
    "Schema 2 is the only supported schema:",
    "The current settings format is:",
    "PRODUCT schema wording",
)
replace_one(
    product,
    "Any omitted currently supported schema-2 setting resolves from the exact current default and is persisted during the next authorized settings write. Unknown, duplicate, nested, invalid, or unsupported content remains an error.",
    "Missing supported settings use the current defaults. Custom keys are left alone.",
    "PRODUCT settings behavior",
)
old_config_section = """The explicit updater supports both existing and missing files:

- existing project or global file: preserve every existing supported value and add every missing current field from the exact default;
- missing project file: use valid global settings when present, use the exact default when the global file is absent, and reject without writing when an existing global file is invalid or unsafe;
- missing global file: `AMS CONFIGURATION UPDATE GLOBAL` may create the exact disabled default;
- complete file: validate and perform no write;
- unknown, duplicate, nested, invalid, or unsupported content: reject without writing.

The updater is never loaded implicitly."""
new_config_section = """The updater preserves existing values, comments, and custom keys while adding missing supported settings from the current defaults. A missing project file starts from readable global values plus defaults, or the exact defaults when no global file exists. The explicit global form may update or create the global file. If the selected file cannot be read or written, it is left unchanged.

The updater is never loaded implicitly."""
replace_one(product, old_config_section, new_config_section, "PRODUCT configuration section")

profile_names = [
    *(f"ams_sol_{e}.toml" for e in ("low", "medium", "high", "xhigh", "max")),
    *(f"ams_terra_{e}.toml" for e in ("low", "medium", "high", "xhigh", "max")),
    *(f"ams_luna_{e}.toml" for e in ("low", "medium", "high", "xhigh", "max")),
    *(f"ams_spark_{e}.toml" for e in ("low", "medium", "high")),
]
required = {
    "SKILL.md",
    "VERSION",
    "agents/openai.yaml",
    "references/configuration-maintenance.md",
    "references/hierarchy-control.md",
    "references/intensity-control.md",
    "references/package-maintenance.md",
    "references/profile-management.md",
    "references/project-control.md",
    "references/project-governance.md",
    "references/root-execution-fallback.md",
    "references/runtime-core.md",
    "references/zergling-rush.md",
    *(f"assets/agent-profiles/{name}" for name in profile_names),
}
observed = {p.relative_to(pkg).as_posix() for p in pkg.rglob("*") if p.is_file()}
if observed != required or len(required) != 31:
    raise SystemExit(
        f"package inventory mismatch: missing={sorted(required-observed)} extra={sorted(observed-required)}"
    )

lines = ["ams-install-manifest-v1", "version\t3.09"]
for rel in sorted(required):
    data = (pkg / rel).read_bytes()
    lines.append(
        f"{hashlib.sha256(data).hexdigest()}\t{len(data)}\tadaptive-master-subagent-orchestration/{rel}"
    )
write(root / "install-manifest.txt", "\n".join(lines))

for path in (skill, project_control, configuration, runtime):
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf") or b"\x00" in data or b"\r" in data or not data.endswith(b"\n"):
        raise SystemExit(f"invalid text encoding or line ending: {path}")

if "Reference trust boundary" in read(skill):
    raise SystemExit("reference validation boundary remains in SKILL")
if "Safe control files" in read(project_control):
    raise SystemExit("control-file validation section remains")
if "Reject duplicate or unknown keys" in read(project_control):
    raise SystemExit("strict settings validation remains")
if "Unknown keys, duplicate keys" in read(configuration):
    raise SystemExit("strict configuration validation remains")

print("MANIFEST_FILES=31")
print(f"SKILL_BYTES={skill.stat().st_size}")
print(f"PROJECT_CONTROL_BYTES={project_control.stat().st_size}")
print(f"CONFIGURATION_MAINTENANCE_BYTES={configuration.stat().st_size}")
print(f"RUNTIME_CORE_BYTES={runtime.stat().st_size}")
