#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).with_name("audit_markdown.py")
text = path.read_text(encoding="utf-8")
old_h1 = '''    if h1_count != 1:
        fail(errors, path, None, f"expected exactly one H1 heading, found {h1_count}")
'''
new_h1 = '''    if path.name == "SKILL.md":
        if h1_count > 1:
            fail(errors, path, None, f"expected at most one H1 heading, found {h1_count}")
    elif h1_count != 1:
        fail(errors, path, None, f"expected exactly one H1 heading, found {h1_count}")
'''
old_paragraph = '''            if compact and not compact.startswith(("#", "-", "*", "|", "```", "~~~", ">")) and len(compact) > 900:
'''
new_paragraph = '''            is_list = bool(re.match(r"^\\d+[.)]\\s", compact))
            if compact and not is_list and not compact.startswith(("#", "-", "*", "|", "```", "~~~", ">")) and len(compact) > 900:
'''
for old, new in ((old_h1, new_h1), (old_paragraph, new_paragraph)):
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit(f"Expected Markdown audit block was not found: {old!r}")
path.write_text(text, encoding="utf-8", newline="\n")
print("Markdown audit rules corrected.")
