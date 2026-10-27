#!/usr/bin/env python3
"""Static inventory of a Bubble app from its .bubble export.

    python3 -I inventory.py app.bubble -o .migration/

Writes inventory.json (machine-readable, every item has a `ref`) and
inventory.md (for reading). Standard library only. Reads the file; runs
nothing. The export can hold API keys: this script never prints values of
API Connector headers, parameters or bodies, only call names and URLs.
"""

import argparse
import json
import pathlib
import re
import sys

SKIP_ACTION_PROPS = {"condition", "action_disabled", "workflow_disabled", "breakpoint"}
EFFECT_ACTIONS = {
    "SendEmail": "email", "SendPasswordResetEmail": "email", "SendConfirmationEmail": "email",
    "SendMagicLink": "email", "SendICSFileEmail": "email", "SendPushNotification": "push",
    "DeleteThing": "delete", "DeleteListOfThings": "delete",
    "ScheduleAPIEvent": "schedule", "ScheduleAPIEventOnList": "schedule", "SetRecurringEvent": "schedule",
    "OpenURL": "external", "DownloadDataAsCSV": "export",
}


def vals(m):
    """Dict entries of a Bubble map; exports mix in counters and other scalars."""
    return [v for v in m.values() if isinstance(v, dict)] if isinstance(m, dict) else []


class App:
    def __init__(self, data):
        self.d = data
        self.types = data.get("user_types") or {}
        self.option_sets = data.get("option_sets") or {}
        self.pages = data.get("pages") or {}
        defs = data.get("element_definitions") or {}
        # Instances name their definition by its `id`, which can differ from its map key.
        self.reusables = {v.get("id", k): v for k, v in defs.items() if isinstance(v, dict)}
        self.names = {}  # element id -> label
        self.page_of = {}  # element id -> root name
        for kind, roots in (("page", self.pages), ("reusable", self.reusables)):
            for root in vals(roots):
                if not isinstance(root, dict):
                    continue
                self.names[root.get("id")] = root.get("name") or root.get("display") or root.get("id")
                for e in self.elements(root):
                    self.names[e["id"]] = self.label(e)
                    self.page_of[e["id"]] = root.get("name") or root.get("display")

    # helpers

    def elements(self, node):
        for e in vals(node.get("elements")):
            if isinstance(e, dict) and e.get("id"):
                yield e
                yield from self.elements(e)

    def reusable_of(self, e):
        """The reusable definition id an element instantiates, if any."""
        rid = (e.get("properties") or {}).get("custom_id") if e.get("type") == "CustomElement" else e.get("type")
        return rid if rid in self.reusables else None

    def label(self, e):
        p = e.get("properties") or {}
        text = p.get("text") or p.get("placeholder")
        t = self.render(text) if text is not None else ""
        name = e.get("name") or e.get("default_name") or e.get("type")
        if self.reusable_of(e):
            r = self.reusables[self.reusable_of(e)]
            name = f"{r.get('name') or r.get('display')} (reusable)"
        return f"{name} \"{t[:40]}\"" if t else name

    def type_name(self, key):
        if not isinstance(key, str):
            return str(key)
        if key.startswith("custom."):
            k = key[7:]
            return (self.types.get(k) or {}).get("display", k)
        if key.startswith("option."):
            k = key[7:]
            return "option " + (self.option_sets.get(k) or {}).get("display", k)
        if key.startswith("list."):
            return "list of " + self.type_name(key[5:])
        return key

    def field_name(self, key):
        for t in vals(self.types):
            f = (t.get("fields") or {}).get(key)
            if f:
                return f.get("display", key)
        return re.sub(r"_(text|number|boolean|date|user|image|file|option_\w+|custom_\w+|list_\w+)$", "", key) if isinstance(key, str) else key

    def render(self, x, depth=0):
        """A readable one-line form of a Bubble expression."""
        if depth > 12:
            return "…"
        if not isinstance(x, dict):
            return json.dumps(x) if not isinstance(x, str) else x
        t = x.get("type")
        p = x.get("properties") or {}
        if t == "TextExpression":
            ents = x.get("entries") or {}
            vals = ents.values() if isinstance(ents, dict) else ents
            s = "".join(v if isinstance(v, str) else "[" + self.render(v, depth + 1) + "]" for v in vals)
        elif t == "CurrentUser":
            s = "Current User"
        elif t == "CurrentPageItem":
            s = "page's thing"
        elif t == "ElementParent":
            s = "parent's thing"
        elif t == "InjectedValue":
            s = "this thing"
        elif t == "GetElement":
            s = self.names.get(p.get("element_id"), p.get("element_id"))
        elif t == "OneOptionValue":
            s = f"{self.type_name(p.get('option_set'))}={p.get('option_value')}"
        elif t == "AllOptionValue":
            s = f"all {self.type_name(p.get('option_set'))}"
        elif t == "Search":
            cons = p.get("constraints") or {}
            cs = [f"{self.field_name(c.get('key'))} {c.get('constraint_type')} {self.render(c.get('value'), depth + 1)}".strip()
                  for c in (cons.values() if isinstance(cons, dict) else cons) if isinstance(c, dict)]
            s = f"Search {self.type_name(p.get('type_to_find'))}" + (f" ({'; '.join(cs)})" if cs else "")
            if p.get("sort_field"):
                s += f" sorted by {self.field_name(p['sort_field'])}{' desc' if p.get('descending') else ''}"
        elif t == "PageData":
            s = p.get("name", "page data")
        elif t == "GetParamFromUrl":
            s = f"URL parameter {p.get('parameter_name', '')}"
        elif t == "CurrentWorkflowItem":
            s = "workflow input" + (f" {p.get('param_id')}" if p.get("param_id") else "")
        elif t == "PreviousStep":
            s = "result of an earlier step"
        elif t == "Message":
            s = ""
        else:
            s = t or "?"
        n = x.get("next")
        while isinstance(n, dict):
            name = n.get("name", "")
            if name.startswith("custom."):
                name = "state " + name[7:].rstrip("_")
            else:
                name = self.field_name(name)
            arg = n.get("args")
            s += f"'s {name}" + (f"({self.render(arg, depth + 1)})" if arg is not None else "")
            n = n.get("next")
        return s

    def page_id(self, pid):
        for p in vals(self.pages):
            if p.get("id") == pid:
                return p.get("name")
        return pid

    # sections

    def workflows(self, root, where):
        out = []
        for wf in vals(root.get("workflows")):
            p = wf.get("properties") or {}
            trigger = wf.get("type")
            if p.get("element_id"):
                trigger += " on " + self.names.get(p["element_id"], p["element_id"])
            actions = []
            for a in vals(wf.get("actions")):
                ap = a.get("properties") or {}
                detail = {}
                for k, v in ap.items():
                    if k in SKIP_ACTION_PROPS:
                        continue
                    if k in ("changes", "initial_values") and isinstance(v, dict):
                        detail[k] = {self.field_name(c.get("key")): self.render(c.get("value"))
                                     for c in v.values() if isinstance(c, dict)}
                    elif k == "element_id" and a.get("type") == "ChangePage":
                        detail["to_page"] = self.page_id(v)
                    elif k == "element_id":
                        detail["element"] = self.names.get(v, v)
                    elif k in ("thing_type", "type_to_change"):
                        detail[k] = self.type_name(v)
                    else:
                        detail[k] = self.render(v) if isinstance(v, dict) else v
                act = {"type": a.get("type"), "detail": detail}
                if ap.get("condition") is not None:
                    act["only_when"] = self.render(ap["condition"])
                if a.get("type") in EFFECT_ACTIONS:
                    act["effect"] = EFFECT_ACTIONS[a.get("type")]
                actions.append(act)
            item = {"ref": f"wf:{where}/{wf.get('id')}", "where": where, "trigger": trigger, "actions": actions}
            if p.get("condition") is not None:
                item["only_when"] = self.render(p["condition"])
            if p.get("wf_name"):
                item["name"] = p["wf_name"]
            out.append(item)
        return out

    def ui(self, root):
        out = []
        for e in self.elements(root):
            p = e.get("properties") or {}
            item = {"element": self.names[e["id"]], "type": e.get("type")}
            interesting = e.get("type") in ("Button", "Link", "Input", "MultiLineInput", "Dropdown", "RepeatingGroup",
                                             "PictureInput", "FileInput", "Checkbox", "DateInput", "Popup", "RadioButtons")
            if e.get("type") == "Link":
                item["to_page"] = self.page_id(p.get("page")) if p.get("linktype") != "url" else self.render(p.get("url"))
            if e.get("type") in ("RepeatingGroup", "Dropdown") and p.get("data_source") is not None:
                item["shows"] = self.render(p["data_source"])
            if p.get("is_visible") is False:
                item["hidden_on_load"] = True
            conds = [self.render(s.get("condition")) + " → " + ", ".join(f"{k}={v}" for k, v in (s.get("properties") or {}).items()
                                                                    if k in ("is_visible", "text", "data_source") and not isinstance(v, dict))
                     for s in vals(e.get("states")) if isinstance(s, dict)]
            conds = [c for c in conds if not c.endswith("→ ")]
            if conds:
                item["conditions"] = conds
            if interesting or conds or item.get("hidden_on_load"):
                out.append(item)
        return out

    def links_into(self):
        inbound = {p.get("name"): set() for p in vals(self.pages)}
        used_on = {}  # reusable id -> pages
        for p in vals(self.pages):
            for e in self.elements(p):
                if self.reusable_of(e):
                    used_on.setdefault(self.reusable_of(e), set()).add(p.get("name"))

        def scan(root, origin_pages):
            for e in self.elements(root):
                pr = e.get("properties") or {}
                if e.get("type") == "Link" and pr.get("page"):
                    for o in origin_pages:
                        inbound.setdefault(self.page_id(pr["page"]), set()).add(o)
            for wf in vals(root.get("workflows")):
                for a in vals(wf.get("actions")):
                    if a.get("type") == "ChangePage":
                        tgt = (a.get("properties") or {}).get("element_id")
                        for o in origin_pages:
                            inbound.setdefault(self.page_id(tgt), set()).add(o)

        for p in vals(self.pages):
            scan(p, [p.get("name")])
        for rid, r in ((k, v) for k, v in self.reusables.items() if isinstance(v, dict)):
            scan(r, sorted(used_on.get(rid, [])) or [f"reusable {r.get('name')}"])
        return {k: sorted(v - {k}) for k, v in inbound.items()}, used_on

    def build(self):
        inbound, used_on = self.links_into()
        pages = []
        for p in sorted(vals(self.pages), key=lambda p: p.get("name") or ""):
            name = p.get("name")
            pp = p.get("properties") or {}
            pages.append({
                "ref": f"page:{name}", "name": name, "title": self.render(pp.get("title")) if pp.get("title") else None,
                "page_thing": self.type_name(pp.get("page_item_type")) if pp.get("page_item_type") else None,
                "reached_from": inbound.get(name, []),
                "custom_states": [s.get("display") or k for k, s in (p.get("custom_states") or {}).items()],
                "ui": self.ui(p), "workflows": self.workflows(p, name),
            })
        reusables = [{"ref": f"reusable:{r.get('name')}", "name": r.get("name"), "used_on": sorted(used_on.get(rid, [])),
                      "ui": self.ui(r), "workflows": self.workflows(r, r.get("name"))}
                     for rid, r in self.reusables.items() if isinstance(r, dict)]
        backend = self.workflows({"workflows": self.d.get("api") or {}}, "backend")
        created = {a["detail"].get("thing_type") for w in [w for p in pages for w in p["workflows"]] + backend
                   + [w for r in reusables for w in r["workflows"]] for a in w["actions"] if a["type"] == "NewThing"}
        types = []
        for key, t in sorted((k, v) for k, v in self.types.items() if isinstance(v, dict)):
            rules = []
            for rk, r in (t.get("privacy_role") or {}).items():
                perm = r.get("permissions") or {}
                rules.append({"rule": r.get("display", rk),
                              "when": "everyone else" if rk == "everyone" else self.render(r.get("condition")),
                              "view_all": perm.get("view_all"), "find_in_searches": perm.get("search_for"),
                              "visible_fields": [self.field_name(f) for f in (perm.get("view_fields") or {}).values()]
                              if not perm.get("view_all") else "all"})
            types.append({"ref": f"type:{t.get('display', key)}", "name": t.get("display", key),
                          "fields": {f.get("display", fk): self.type_name(f.get("value")) + (" (list)" if str(f.get("value", "")).startswith("list.") else "")
                                     for fk, f in (t.get("fields") or {}).items() if not f.get("deleted")},
                          "privacy": rules, "created_by_a_workflow": t.get("display", key) in created or key == "user"})
        options = [{"ref": f"option:{o.get('display', k)}", "name": o.get("display", k),
                    "values": [v.get("display") for v in sorted(vals(o.get("values")), key=lambda v: v.get("sort_factor", 0)) if not v.get("deleted")]}
                   for k, o in sorted(self.option_sets.items()) if isinstance(o, dict)]
        cs = (self.d.get("settings") or {}).get("client_safe") or {}
        calls = []
        for g in vals(cs.get("apiconnector2")):
            for c in vals(g.get("calls")):
                if c.get("url"):
                    calls.append({"ref": f"call:{g.get('human')}/{c.get('name')}", "group": g.get("human"), "name": c.get("name"),
                                  "method": c.get("method"), "url": re.sub(r"\?.*", "?…", str(c.get("url"))), "use_as": c.get("publish_as")})
        effects = [{"where": w["where"], "trigger": w["trigger"], "effect": a["effect"], "action": a["type"], "detail": a["detail"]}
                   for w in [w for p in pages for w in p["workflows"]] + [w for r in reusables for w in r["workflows"]] + backend
                   for a in w["actions"] if a.get("effect")]
        hints = [f"page `{p['name']}` has no link or navigation into it" for p in pages
                 if not p["reached_from"] and p["name"] not in ("index", "404", "reset_pw")]
        hints += [f"type `{t['name']}` is never created by a workflow" for t in types if not t["created_by_a_workflow"]]
        return {
            "app": {"password_protected": bool(cs.get("pw_protection")), "plugins": sorted((cs.get("plugins") or {}).keys())},
            "pages": pages, "reusables": reusables, "backend_workflows": backend, "data_types": types,
            "option_sets": options, "api_calls": calls, "side_effects": effects, "dead_feature_hints": hints,
        }


def markdown(inv):
    L = ["# Inventory", "", "Static read of the export. Refs in backticks are the coverage targets.", ""]
    a = inv["app"]
    L += [f"Password protected: {a['password_protected']}. Plugins: {', '.join(a['plugins']) or 'none'}.", ""]
    L += ["## Pages", ""]
    for p in inv["pages"]:
        L.append(f"### `{p['ref']}`")
        L.append(f"Page thing: {p['page_thing'] or '-'}. Reached from: {', '.join(p['reached_from']) or 'nowhere'}."
                 + (f" Custom states: {', '.join(p['custom_states'])}." if p["custom_states"] else ""))
        for u in p["ui"]:
            bits = [f"- {u['type']} {u['element']}"]
            for k in ("to_page", "shows"):
                if u.get(k):
                    bits.append(f"{k.replace('_', ' ')}: {u[k]}")
            if u.get("hidden_on_load"):
                bits.append("hidden on load")
            if u.get("conditions"):
                bits.append("when " + " | ".join(u["conditions"]))
            L.append("; ".join(bits))
        for w in p["workflows"]:
            L += wf_md(w)
        L.append("")
    for title, key in (("Reusable elements", "reusables"),):
        L += [f"## {title}", ""]
        for r in inv[key]:
            L.append(f"### `{r['ref']}` (on {', '.join(r['used_on']) or 'no page'})")
            for u in r["ui"]:
                L.append(f"- {u['type']} {u['element']}" + (f"; when {' | '.join(u['conditions'])}" if u.get("conditions") else ""))
            for w in r["workflows"]:
                L += wf_md(w)
            L.append("")
    L += ["## Backend workflows", ""] + ([x for w in inv["backend_workflows"] for x in wf_md(w)] or ["none"]) + [""]
    L += ["## Data types", ""]
    for t in inv["data_types"]:
        L.append(f"### `{t['ref']}`")
        L.append("Fields: " + ", ".join(f"{k} ({v})" for k, v in t["fields"].items()))
        for r in t["privacy"]:
            vis = "all fields" if r["visible_fields"] == "all" else ("fields " + ", ".join(r["visible_fields"]) if r["visible_fields"] else "no fields")
            L.append(f"- privacy `{r['rule']}` when {r['when']}: {vis}; in searches: {r['find_in_searches']}")
        L.append("")
    L += ["## Option sets", ""] + [f"- `{o['ref']}`: {', '.join(o['values'])}" for o in inv["option_sets"]] + [""]
    L += ["## API calls", ""] + ([f"- `{c['ref']}` {c['method']} {c['url']} ({c['use_as']})" for c in inv["api_calls"]] or ["none"]) + [""]
    L += ["## Side effects", ""] + ([f"- {e['effect']}: {e['action']} in {e['where']} on {e['trigger']}" for e in inv["side_effects"]] or ["none"]) + [""]
    L += ["## Dead-feature hints", ""] + ([f"- {h}" for h in inv["dead_feature_hints"]] or ["none"]) + [""]
    return "\n".join(L)


def wf_md(w):
    head = f"- workflow `{w['ref']}`{(' ' + w['name']) if w.get('name') else ''}: {w['trigger']}" + (f", only when {w['only_when']}" if w.get("only_when") else "")
    out = [head]
    for a in w["actions"]:
        det = "; ".join(f"{k}: {json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}" for k, v in a["detail"].items())
        out.append(f"  - {a['type']}{(' — ' + det) if det else ''}" + (f" (only when {a['only_when']})" if a.get("only_when") else ""))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export")
    ap.add_argument("-o", "--out", default=".migration")
    args = ap.parse_args()
    data = json.loads(pathlib.Path(args.export).read_text())
    if not isinstance(data, dict) or "pages" not in data:
        sys.exit("not a Bubble app export (no `pages`)")
    inv = App(data).build()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "inventory.json").write_text(json.dumps(inv, indent=1, ensure_ascii=False))
    (out / "inventory.md").write_text(markdown(inv))
    n = sum(len(p["workflows"]) for p in inv["pages"]) + len(inv["backend_workflows"])
    print(f"{len(inv['pages'])} pages, {n} workflows, {len(inv['data_types'])} types, "
          f"{len(inv['api_calls'])} API calls, {len(inv['dead_feature_hints'])} dead-feature hints -> {out}/inventory.md")


if __name__ == "__main__":
    main()
