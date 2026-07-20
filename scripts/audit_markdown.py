#!/usr/bin/env python3
"""Audit every Markdown file for structure, readability, and broken local links."""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
USER_DOC_NAMES = {
    "README.md",
    "INSTALLATION.md",
    "INSTALLER-USAGE.md",
    "INSTALLER-AUDIT.md",
    "MANUAL-INSTALLATION.md",
    "AUDIT.md",
    "CHANGELOG.md",
}
FORBIDDEN_PHRASES = (
    "when the repository is public",
    "while the repository is private",
    "private-repository commands",
    "repository remains private",
    "public download",
    "private download",
    "ultra is an orchestration classification",
    "ultra-shaped",
    "adaptive-master-subagent-orchestration-all-options-v3.1.0.zip",
)
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
BAD_HEADING_RE = re.compile(r"^#{1,6}[^#\s]")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")


def fail(errors: list[str], path: Path, line: int | None, message: str) -> None:
    relative = path.relative_to(ROOT).as_posix()
    where = f"{relative}:{line}" if line is not None else relative
    errors.append(f"{where}: {message}")


def github_slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[`*_~]", "", text)
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = "".join(ch for ch in text if ch.isalnum() or ch in " -_")
    text = re.sub(r"[ _]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def markdown_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    in_fence: tuple[str, int] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        match = FENCE_RE.match(line)
        if match:
            marker = match.group(2)
            if in_fence is None:
                in_fence = (marker[0], len(marker))
            elif marker[0] == in_fence[0] and len(marker) >= in_fence[1] and not match.group(3).strip():
                in_fence = None
            continue
        if in_fence:
            continue
        heading = HEADING_RE.match(line)
        if not heading:
            continue
        base = github_slug(heading.group(2))
        count = counts.get(base, 0)
        counts[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def split_table_row(line: str) -> list[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    code = False
    for char in value:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            current.append(char)
            escaped = True
        elif char == "`":
            current.append(char)
            code = not code
        elif char == "|" and not code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    cells.append("".join(current).strip())
    return cells


def link_target(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")]
    if " \"" in raw or " '" in raw:
        raw = raw.split(maxsplit=1)[0]
    return raw


def audit_file(path: Path, errors: list[str], anchor_cache: dict[Path, set[str]]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        fail(errors, path, None, f"not valid UTF-8: {exc}")
        return
    if "\x00" in text:
        fail(errors, path, None, "contains a NUL byte")
    if text and not text.endswith("\n"):
        fail(errors, path, None, "missing final newline")

    lowered = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            fail(errors, path, None, f"contains stale or confusing wording: {phrase!r}")

    lines = text.splitlines()
    in_fence: tuple[str, int, int] | None = None
    h1_count = 0
    previous_heading = 0
    table_widths: dict[int, int] = {}

    for number, line in enumerate(lines, start=1):
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(2)
            if in_fence is None:
                in_fence = (marker[0], len(marker), number)
            elif marker[0] == in_fence[0] and len(marker) >= in_fence[1] and not fence.group(3).strip():
                in_fence = None
            continue
        if in_fence:
            continue

        if line.rstrip() != line:
            fail(errors, path, number, "trailing whitespace")
        if "\t" in line:
            fail(errors, path, number, "tab character outside a code fence")
        if BAD_HEADING_RE.match(line):
            fail(errors, path, number, "heading marker must be followed by a space")

        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            if level == 1:
                h1_count += 1
            if path.name in USER_DOC_NAMES and previous_heading and level > previous_heading + 1:
                fail(errors, path, number, f"heading level jumps from H{previous_heading} to H{level}")
            previous_heading = level

        if TABLE_SEPARATOR_RE.match(line):
            if number == 1:
                fail(errors, path, number, "table separator has no header row")
            else:
                width = len(split_table_row(lines[number - 2]))
                separator_width = len(split_table_row(line))
                if width < 2 or width != separator_width:
                    fail(errors, path, number, "table header and separator have different column counts")
                table_widths[number] = width
        elif table_widths and "|" in line:
            active = max(table_widths)
            if active < number and line.strip():
                width = table_widths[active]
                if len(split_table_row(line)) != width:
                    fail(errors, path, number, f"table row has a different column count than the header ({width})")
        elif not line.strip():
            table_widths.clear()

        for match in LINK_RE.finditer(line):
            target = link_target(match.group(1))
            if not target or target.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            decoded = unquote(target)
            file_part, separator, fragment = decoded.partition("#")
            destination = path if not file_part else (path.parent / file_part).resolve(strict=False)
            try:
                destination.relative_to(ROOT.resolve())
            except ValueError:
                fail(errors, path, number, f"local link escapes the repository: {target}")
                continue
            if not destination.exists():
                fail(errors, path, number, f"broken local link: {target}")
                continue
            if fragment and destination.is_file() and destination.suffix.lower() == ".md":
                anchors = anchor_cache.setdefault(destination, markdown_anchors(destination))
                if fragment not in anchors:
                    fail(errors, path, number, f"broken Markdown anchor: {target}")

    if in_fence:
        fail(errors, path, in_fence[2], "unclosed fenced code block")
    if h1_count != 1:
        fail(errors, path, None, f"expected exactly one H1 heading, found {h1_count}")

    if path.name in USER_DOC_NAMES:
        paragraphs = re.split(r"\n\s*\n", text)
        for paragraph in paragraphs:
            compact = " ".join(paragraph.split())
            if compact and not compact.startswith(("#", "-", "*", "|", "```", "~~~", ">")) and len(compact) > 900:
                fail(errors, path, None, "contains a paragraph longer than 900 characters; split it for readability")


def main() -> int:
    markdown_files = sorted(path for path in ROOT.rglob("*.md") if ".git" not in path.parts)
    if not markdown_files:
        raise SystemExit("No Markdown files found")
    errors: list[str] = []
    anchor_cache: dict[Path, set[str]] = {}
    for path in markdown_files:
        audit_file(path, errors, anchor_cache)
    if errors:
        print("MARKDOWN AUDIT FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"MARKDOWN AUDIT PASSED: {len(markdown_files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
