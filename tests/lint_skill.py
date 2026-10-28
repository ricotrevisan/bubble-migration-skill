#!/usr/bin/env python3
"""Lint the skill's own files. Run in CI: python3 -I tests/lint_skill.py

- SKILL.md frontmatter must parse as strict YAML: an unquoted value that
  contains ": " starts a new mapping and breaks GitHub and other parsers.
- Every relative link in the skill's markdown must point at a file.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
problems = []

text = (ROOT / "SKILL.md").read_text()
m = re.match(r"---\n(.*?)\n---\n", text, re.S)
if not m:
    problems.append("SKILL.md: no frontmatter")
else:
    keys = {}
    for n, line in enumerate(m.group(1).splitlines(), 2):
        km = re.match(r"([a-z][a-z0-9_-]*): (.*)$", line)
        if not km:
            problems.append(f"SKILL.md:{n}: not a `key: value` line")
            continue
        key, val = km.groups()
        keys[key] = val
        quoted = len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'"
        if not quoted and (": " in val or " #" in val or val[:1] in "[{&*!|>%@`"):
            problems.append(f"SKILL.md:{n}: unquoted `{key}` contains YAML syntax; wrap the value in double quotes")
    for key in ("name", "description"):
        if key not in keys:
            problems.append(f"SKILL.md: frontmatter lacks `{key}`")

for md in ROOT.rglob("*.md"):
    if ".git" in md.parts:
        continue
    for target in re.findall(r"\]\(([^)#\s]+)\)", md.read_text()):
        if "://" in target:
            continue
        if not (md.parent / target).exists():
            problems.append(f"{md.relative_to(ROOT)}: broken link {target}")

for p in problems:
    print("-", p)
print(f"{len(problems)} problems" if problems else "OK")
sys.exit(1 if problems else 0)
