#!/usr/bin/env python3
"""Check a .migration/ folder against the contract and write coverage.md.

    python3 -I check.py .migration

Exits 0 when the backlog passes, 1 with a list of problems otherwise.
Standard library only.
"""

import json
import pathlib
import re
import sys

UI_ONLY = {"ShowElement", "HideElement", "ToggleElement", "SetCustomState", "AnimateElement",
           "ScrollToElement", "ResetInputs", "ResetGroup", "DisplayGroupData", "SetFocus"}
BUBBLE_TERMS = re.compile(r"\b(repeating ?groups?|custom states?|option sets?|data types?|reusable elements?|"
                          r"workflows?|things?|page is loaded|dynamic expression)\b", re.I)
REQUIRED = ["id", "title", "persona", "epic", "priority", "status", "evidence", "inventory_refs"]


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        return None, text
    meta = {}
    for line in m.group(1).splitlines():
        line = re.sub(r"\s+#.*$", "", line)
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
            meta[k.strip()] = v
    return meta, m.group(2)


def behavioural(wf):
    return any(a.get("type") not in UI_ONLY for a in wf.get("actions", []))


def main(root):
    root = pathlib.Path(root)
    problems = []
    need = ["inputs.md", "inventory.json", "evidence/journal.md", "personas.md", "decisions.md",
            "open-questions.md", "data-model.md", "workflows.md", "integrations.md"]
    for n in need:
        if not (root / n).exists():
            problems.append(f"missing {n}")

    inv = json.loads((root / "inventory.json").read_text()) if (root / "inventory.json").exists() else {}
    refs = set()
    targets = {}  # ref -> what it is; the coverage checklist
    for p in inv.get("pages", []):
        refs.add(p["ref"])
        if p["name"] != "404":
            targets[p["ref"]] = "page"
        for w in p["workflows"]:
            refs.add(w["ref"])
            if behavioural(w):
                targets[w["ref"]] = "workflow"
    for r in inv.get("reusables", []):
        refs.add(r["ref"])
        for w in r["workflows"]:
            refs.add(w["ref"])
            if behavioural(w):
                targets[w["ref"]] = "workflow"
    for w in inv.get("backend_workflows", []):
        refs.add(w["ref"])
        targets[w["ref"]] = "backend workflow"
    for t in inv.get("data_types", []):
        refs.add(t["ref"])
        targets[t["ref"]] = "data type"
    for c in inv.get("api_calls", []):
        refs.add(c["ref"])
        targets[c["ref"]] = "API call"
    for o in inv.get("option_sets", []):
        refs.add(o["ref"])

    journal = (root / "evidence/journal.md").read_text() if (root / "evidence/journal.md").exists() else ""
    entries = set(re.findall(r"^##\s+(E\d+)", journal, re.M))
    personas_md = (root / "personas.md").read_text() if (root / "personas.md").exists() else ""
    personas = {h.strip().lower() for h in re.findall(r"^##\s+(.+)$", personas_md, re.M)} | {"system"}

    stories = sorted((root / "stories").glob("*.md")) if (root / "stories").exists() else []
    if not stories:
        problems.append("no stories in stories/")
    cited = {}
    ids = set()
    for f in stories:
        meta, body = frontmatter(f.read_text())
        where = f"stories/{f.name}"
        if meta is None:
            problems.append(f"{where}: no frontmatter")
            continue
        for k in REQUIRED:
            if k not in meta:
                problems.append(f"{where}: missing `{k}`")
        if meta.get("id") in ids:
            problems.append(f"{where}: duplicate id {meta.get('id')}")
        ids.add(meta.get("id"))
        ev = meta.get("evidence") if isinstance(meta.get("evidence"), list) else []
        ir = meta.get("inventory_refs") if isinstance(meta.get("inventory_refs"), list) else []
        if meta.get("priority") not in ("must", "should", "could"):
            problems.append(f"{where}: priority must be must, should or could")
        status = meta.get("status")
        if status not in ("observed", "inferred", "drop-candidate"):
            problems.append(f"{where}: status must be observed, inferred or drop-candidate")
        if status == "observed" and not ev:
            problems.append(f"{where}: observed story without evidence")
        if status == "inferred" and not ir:
            problems.append(f"{where}: inferred story without inventory_refs")
        if str(meta.get("persona", "")).lower() not in personas:
            problems.append(f"{where}: persona `{meta.get('persona')}` has no heading in personas.md")
        for e in ev:
            if e not in entries:
                problems.append(f"{where}: evidence {e} is not in evidence/journal.md")
        for r in ir:
            if inv and r not in refs:
                problems.append(f"{where}: inventory ref {r} is not in inventory.json")
            cited.setdefault(r, []).append(meta.get("id"))
        if not re.search(r"\bAs an? .+\bI want\b.+\bso that\b", body, re.I | re.S):
            problems.append(f"{where}: no 'As a … I want … so that …' sentence")
        if not re.search(r"```gherkin.*?Scenario:.*?```", body, re.S):
            problems.append(f"{where}: no gherkin block with a Scenario")
        for m in BUBBLE_TERMS.finditer(meta.get("title", "") + "\n" + body):
            problems.append(f"{where}: Bubble term `{m.group(0)}`; use the app's domain words")

    notes = (root / "coverage-notes.md").read_text() if (root / "coverage-notes.md").exists() else ""
    explained = set(re.findall(r"`([a-z]+:[^`]+)`", notes))
    lines = ["# Coverage", "", "Written by check.py. Every inventory target is covered by a story or explained in coverage-notes.md.", "",
             "| ref | kind | covered by |", "|---|---|---|"]
    uncovered = []
    for ref, kind in sorted(targets.items()):
        if ref in cited:
            by = ", ".join(sorted(set(cited[ref])))
        elif ref in explained:
            by = "coverage-notes.md"
        else:
            by = "**nothing**"
            uncovered.append(ref)
        lines.append(f"| `{ref}` | {kind} | {by} |")
    covered = len(targets) - len(uncovered)
    lines[2] += f" {covered}/{len(targets)} covered."
    (root / "coverage.md").write_text("\n".join(lines) + "\n")
    for ref in uncovered:
        problems.append(f"coverage: {targets[ref]} `{ref}` has no story and no line in coverage-notes.md")

    if problems:
        print(f"{len(problems)} problems:")
        for p in problems:
            print(" -", p)
        return 1
    print(f"OK: {len(stories)} stories, {covered}/{len(targets)} inventory targets covered.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ".migration"))
