from pathlib import Path
import hashlib
import tomllib
import zipfile

ROOT = Path.cwd()
PKG = ROOT / "adaptive-master-subagent-orchestration"
ZIP = ROOT / "adaptive-master-subagent-orchestration-3.09.zip"
TMP = ROOT / ".github/ams-fix"
OLD = "f35aa28cad7c2691e80823e36ca276cbee8b20de067600fd8edb8f2aaf10fe4b"


def read(name):
    return (TMP / name).read_text(encoding="utf-8").rstrip() + "\n"


def write(path, text):
    path.write_text(text.rstrip("\r\n") + "\n", encoding="utf-8", newline="\n")


def section(text, start, end, replacement, label):
    a = text.find(start)
    b = text.find(end, a + len(start))
    if a < 0 or b < 0 or text.find(start, a + 1) >= 0:
        raise SystemExit(f"bad {label} markers")
    return text[:a] + replacement.rstrip() + "\n\n" + text[b:]


def replace_required(text, old, new, label):
    count = text.count(old)
    if count < 1:
        raise SystemExit(f"missing {label}")
    return text.replace(old, new)


readme_path = ROOT / "README.md"
readme = readme_path.read_text(encoding="utf-8")
readme = section(readme, "## Start using AMS", "## Intensity modes", read("README_START.md"), "README")
readme = replace_required(
    readme,
    "AMS ENABLE\nAMS DISABLE\nAMS MODE auto|minimal|balanced|moderate|heavy|extreme",
    "AMS STATUS\nAMS ENABLE\nAMS DISABLE\nAMS MODE auto|minimal|balanced|moderate|heavy|extreme",
    "README command list",
)
write(readme_path, readme)

install_doc = ROOT / "INSTALLATION.md"
text = install_doc.read_text(encoding="utf-8")
text = section(text, "## Start using AMS", "## Agent profiles", read("INSTALLATION_START.md"), "INSTALLATION")
text = text.replace(
    "Project settings and installed profiles are preserved intentionally.",
    "Project settings, manually created global settings, and installed profiles are preserved intentionally.",
)
write(install_doc, text)

product_path = ROOT / "PRODUCT DOCUMENTATION.md"
text = product_path.read_text(encoding="utf-8")
text = text.replace(
    "AMS is project-specific. Persistent settings for one project do not enable AMS in another project.",
    "Project commands remain project-specific. A manually created global settings file can supply defaults to trusted projects that do not have project settings.",
)
text = section(text, "## Starting and stopping AMS", "## Project settings", read("PRODUCT_STARTING.md"), "product starting")
text = section(text, "## Project settings", "## Command reference", read("PRODUCT_SETTINGS.md"), "product settings")
text = section(text, "## Command reference", "## Intensity modes", read("PRODUCT_COMMANDS.md"), "product commands")
text = text.replace(
    "When `CODEX_HOME` is unset, the installer uses `$HOME/.codex/agents/`.\n\n### Project settings and optional recovery",
    "When `CODEX_HOME` is unset, the installer uses `$HOME/.codex/agents/`.\n\n### Global settings (manual only)\n\n```text\n$CODEX_HOME/ams-orchestration.toml\n```\n\nWhen `CODEX_HOME` is unset, use `$HOME/.codex/ams-orchestration.toml`.\n\n### Project settings and optional recovery",
)
text = text.replace(
    "Standard uninstall removes only the AMS skill directory. It preserves project settings, recovery state, generated or installed AMS profiles, and unrelated skills.",
    "Standard uninstall removes only the AMS skill directory. It preserves project settings, manually created global settings, recovery state, generated or installed AMS profiles, and unrelated skills.",
)
write(product_path, text)

expected = [
    "SKILL.md", "VERSION", "agents/openai.yaml",
    "references/hierarchy-control.md", "references/intensity-control.md",
    "references/package-maintenance.md", "references/profile-management.md",
    "references/project-control.md", "references/runtime-core.md",
    "references/zergling-rush.md",
]
for family in ("sol", "terra", "luna"):
    for effort in ("low", "medium", "high", "xhigh", "max"):
        expected.append(f"assets/agent-profiles/ams_{family}_{effort}.toml")
for effort in ("low", "medium", "high"):
    expected.append(f"assets/agent-profiles/ams_spark_{effort}.toml")
expected.sort()
actual = sorted(str(p.relative_to(PKG)).replace("\\", "/") for p in PKG.rglob("*") if p.is_file())
if actual != expected:
    raise SystemExit("package inventory mismatch")

for rel in actual:
    data = (PKG / rel).read_bytes()
    if data.startswith(b"\xef\xbb\xbf") or b"\x00" in data or b"\r" in data or not data.endswith(b"\n"):
        raise SystemExit(f"invalid text: {rel}")
    if rel.endswith(".toml"):
        tomllib.loads(data.decode("utf-8"))

skill = (PKG / "SKILL.md").read_text(encoding="utf-8")
for required in (
    "Bootstrap AMS on every top-level project turn",
    "$CODEX_HOME/ams-orchestration.toml",
    "AMS STATUS",
    "Global persistence is manual only",
):
    if required not in skill:
        raise SystemExit(f"missing SKILL bootstrap text: {required}")

base = "adaptive-master-subagent-orchestration"
dirs = [f"{base}/", f"{base}/agents/", f"{base}/assets/", f"{base}/assets/agent-profiles/", f"{base}/references/"]
if ZIP.exists():
    ZIP.unlink()
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for name in dirs:
        info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.external_attr = (0o40755 << 16) | 0x10
        info.compress_type = zipfile.ZIP_STORED
        z.writestr(info, b"")
    for rel in actual:
        info = zipfile.ZipInfo(f"{base}/{rel}", (1980, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, (PKG / rel).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

new = hashlib.sha256(ZIP.read_bytes()).hexdigest()
with zipfile.ZipFile(ZIP) as z:
    if z.namelist()[:5] != dirs:
        raise SystemExit("zip directory mismatch")
    files = sorted(n for n in z.namelist() if not n.endswith("/"))
    if files != [f"{base}/{rel}" for rel in actual]:
        raise SystemExit("zip file mismatch")
    for rel in actual:
        if z.read(f"{base}/{rel}") != (PKG / rel).read_bytes():
            raise SystemExit(f"zip content mismatch: {rel}")

for path in (ROOT / "install.ps1", ROOT / "install.sh", readme_path, install_doc, product_path):
    write(path, replace_required(path.read_text(encoding="utf-8"), OLD, new, f"checksum in {path.name}"))

for path in (readme_path, install_doc, product_path):
    text = path.read_text(encoding="utf-8")
    for forbidden in ("virtual-hierarchy-final-audited", "ReleaseZip", "/releases/download/"):
        if forbidden in text:
            raise SystemExit(f"stale reference in {path.name}: {forbidden}")
    for required in ("$CODEX_HOME/ams-orchestration.toml", "Global persistence", "AMS STATUS", new):
        if required not in text:
            raise SystemExit(f"missing {required} in {path.name}")

print(f"PACKAGE_SHA256={new}")
print(f"PACKAGE_BYTES={ZIP.stat().st_size}")
