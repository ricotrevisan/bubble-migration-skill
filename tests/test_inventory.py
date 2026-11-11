#!/usr/bin/env python3
"""A Buildprint workspace and the export of the same app give the same inventory.

    python3 -I tests/test_inventory.py

Builds a tiny export, splits it into a fake workspace index the way Buildprint
stores it (one JSON fragment per root, keys in another order), runs
inventory.py on both and compares.
"""
import json
import pathlib
import sqlite3
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "inventory.py"

EXPORT = {
    "pages": {"p1": {"id": "PA", "name": "index", "elements": {
        "e1": {"id": "EA", "type": "Button", "properties": {"text": "Post job"}}},
        "workflows": {"w1": {"id": "WA", "type": "ButtonClicked", "properties": {"element_id": "EA"}, "actions": {
            "1": {"type": "SendEmail", "properties": {"subject": "second"}},
            "0": {"type": "NewThing", "properties": {"thing_type": "custom.job"}},
            "10": {"type": "ChangePage", "properties": {"element_id": "PA"}}}}}}},
    "user_types": {"job": {"display": "Job", "fields": {"title_text": {"display": "Title", "value": "text"}},
                           "privacy_role": {"everyone": {"display": "everyone", "permissions": {"view_all": False}}}}},
    "option_sets": {"role": {"display": "Role", "values": {"a": {"display": "Client", "sort_factor": 1}}}},
    "api": {"b1": {"id": "BA", "type": "APIEvent", "properties": {"wf_name": "nightly"}, "actions": {}}},
    "settings": {"client_safe": {"pw_protection": True, "plugins": {"stripe": True}}},
}


def reorder(x):
    """Same data, reversed key order, as a different serializer would write it."""
    return {k: reorder(x[k]) for k in reversed(list(x))} if isinstance(x, dict) else x


def run(src, out):
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), str(src), "-o", str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads((out / "inventory.json").read_text())


with tempfile.TemporaryDirectory() as d:
    d = pathlib.Path(d)
    (d / "app.bubble").write_text(json.dumps(EXPORT))
    ws = d / "src" / "test"
    (ws / ".buildprint").mkdir(parents=True)
    con = sqlite3.connect(ws / ".buildprint" / "index.sqlite")
    con.execute("CREATE TABLE snapshot_roots (root_key text PRIMARY KEY, identity_key text, json text, content_sha256 text)")
    roots = [("__interface__", {"_id": "x"})] + [
        (f"{top}/{k}", {top: {k: v}}) for top in ("pages", "user_types", "option_sets", "api") for k, v in EXPORT[top].items()]
    roots.append(("settings/app.ts", {"settings": {"client_safe": {}}}))  # Buildprint drops pw_protection and plugins
    con.executemany("INSERT INTO snapshot_roots VALUES (?, ?, ?, '')", [(k, k, json.dumps(reorder(v))) for k, v in roots])
    con.commit()
    con.close()

    a = run(d / "app.bubble", d / "a")
    b = run(d / "src", d / "b")  # parent of the branch folder works too

    problems = []
    acts = [x["type"] for x in a["pages"][0]["workflows"][0]["actions"]]
    if acts != ["NewThing", "SendEmail", "ChangePage"]:
        problems.append(f"actions not in number order: {acts}")
    if a["app"] != {"password_protected": True, "plugins": ["stripe"]}:
        problems.append(f"export app settings: {a['app']}")
    if b["app"] != {"password_protected": None, "plugins": None}:
        problems.append(f"workspace app settings should be unknown: {b['app']}")
    a.pop("app"), b.pop("app")
    if a != b:
        problems.append("workspace and export inventories differ")

for p in problems:
    print("-", p)
print(f"{len(problems)} problems" if problems else "OK")
sys.exit(1 if problems else 0)
