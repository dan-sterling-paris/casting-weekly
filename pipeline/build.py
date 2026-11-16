"""Step 5. Apply the rules to the fetched pages, confirm identities, and write:
  pipeline/out/graph.json        nodes and edges; every edge has its rule, sentence, URL, page hash and fetch time
  pipeline/out/TRACE.md          a step-by-step audit of each worked example, plus coverage counts
  prototype/industry-intel.html  the network view, built from graph.json
No AI anywhere: running it twice on the same pages gives identical output.

Source types (set by a person in seeds.json):
  producer         the producer's own press pages: rules P1/P2 (production) and C1-C6 (credits)
  production-site  a show's official site: the show is named by the seed; rules C1-C6 for credits
  person-site      a person's own site or agent page: used to confirm identity; agent CV layout read by rule A1
"""
import json
import re
from collections import defaultdict
from common import CACHE, OUT, ROOT, seeds
from link import confirm, norm, norm_work
from rules import agent_cv, credits, production

pages = [p for p in json.loads((OUT / "pages.json").read_text()) if p.get("status") == 200]
sources = {s["id"]: s for s in json.loads((OUT / "sources.json").read_text())}
seed = {s["id"]: s for s in seeds()}
text_of = {p["url"]: (CACHE / p["file"]).read_text() for p in pages}
prov_of = {p["url"]: {"url": p["url"], "sha256": p["sha256"], "fetched_at": p["fetched_at"]} for p in pages}

own = defaultdict(str)                       # person -> text of their own site / agent page
for p in pages:
    s = seed[p["seed"]]
    if s["kind"] == "person-site":
        own[norm(s["person"])] += "\n" + text_of[p["url"]]

nodes, edges = {}, []
coverage = {"no_production": [], "title_unreadable": [], "no_credits": [], "official_site_no_credits": []}


def node(nid, kind, label, **kw):
    nodes.setdefault(nid, {"id": nid, "kind": kind, "label": label, **kw})
    return nid


def prod_node(title):
    return node("prod:" + norm_work(title), "production", title)


def org_node(name):
    return node("org:" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"), "organisation", name)


def add_edge(e):
    key = (e["source"], e["target"], e["type"], e.get("role"), e.get("year"))
    if not any((x["source"], x["target"], x["type"], x.get("role"), x.get("year")) == key for x in edges):
        edges.append(e)


def identity(name, title, source_kind):
    if source_kind == "agent":
        return "source is their own agent's page", None
    hit = confirm(title, own.get(norm(name), ""))
    return ("confirmed by own site", hit) if hit else ("name match only", None)


for p in sorted(pages, key=lambda x: x["url"]):
    s, t, prov = seed[p["seed"]], text_of[p["url"]], prov_of[p["url"]]
    if s["kind"] == "producer":
        pr = production(t)
        if not pr:
            coverage["no_production"].append(p["url"]); continue
        rid, title, sent = pr
        if not title:
            coverage["title_unreadable"].append({"url": p["url"], "sentence": sent}); continue
        org, prod = node("org:" + s["id"], "organisation", s["name"].split(" (")[0]), prod_node(title)
        add_edge({"source": org, "target": prod, "type": "produces", "rule": rid, "sentence": sent, **prov})
        found = credits(t)
        if not found:
            coverage["no_credits"].append(p["url"])
        for crid, role, name, csent in found:
            idn, ev = identity(name, title, "page")
            add_edge({"source": node("person:" + norm(name), "person", name), "target": prod, "type": "credit", "role": role,
                      "rule": crid, "sentence": csent, "identity": idn, "identity_evidence": ev, **prov})
    elif s["kind"] == "production-site":
        prod = prod_node(s["production"])
        found = credits(t)
        if not found:
            coverage["official_site_no_credits"].append(p["url"])
        for crid, role, name, csent in found:
            idn, ev = identity(name, s["production"], "page")
            add_edge({"source": node("person:" + norm(name), "person", name), "target": prod, "type": "credit", "role": role,
                      "rule": crid, "sentence": csent, "identity": idn, "identity_evidence": ev, **prov})

# agent pages: only credits for shows already in the network or named in a seed (the shows a person chose)
wanted = {n["id"] for n in nodes.values() if n["kind"] == "production"} | {"prod:" + norm_work(s["production"]) for s in seeds() if s.get("production")}
for p in sorted(pages, key=lambda x: x["url"]):
    s = seed[p["seed"]]
    if s["kind"] != "person-site":
        continue
    for b in agent_cv(text_of[p["url"]]):
        pid = "prod:" + norm_work(b["title"])
        if pid not in wanted:
            continue
        label = next((x["production"] for x in seeds() if x.get("production") and "prod:" + norm_work(x["production"]) == pid), b["title"].title())
        prod = node(pid, "production", label)
        person = node("person:" + norm(s["person"]), "person", s["person"])
        role = "Casting director" if "casting" in b["role"].lower() else b["role"]
        common = {"rule": "A1", "sentence": b["evidence"], "year": b["year"], "venue": b["venue"], **prov_of[p["url"]]}
        add_edge({"source": person, "target": prod, "type": "credit", "role": role, "role_as_stated": b["role"],
                  "identity": "source is their own agent's page", "identity_evidence": None, **common})
        add_edge({"source": org_node(b["venue"]), "target": prod, "type": "staged at", **common})
        for d in b["directors"]:
            add_edge({"source": node("person:" + norm(d), "person", d), "target": prod, "type": "credit", "role": "Director",
                      "identity": "name match only", "identity_evidence": None, **common})

graph = {"method": "pattern rules, no AI", "seeds": [s["id"] for s in seeds()],
         "nodes": sorted(nodes.values(), key=lambda n: n["id"]), "edges": edges, "coverage": coverage}
(OUT / "graph.json").write_text(json.dumps(graph, indent=1, ensure_ascii=False, sort_keys=True))

# ---- the network view ----
label = {n["id"]: n["label"] for n in nodes.values()}
org_edges = defaultdict(list)
for e in edges:
    if e["type"] in ("produces", "staged at"):
        org_edges[e["target"]].append(e)
ui_edges, orgs = [], {}
for e in edges:
    if e["type"] != "credit":
        continue
    oe = next((o for o in org_edges[e["target"]] if o.get("year") == e.get("year")), None) or (org_edges[e["target"]] or [None])[0]
    oid = oe["source"].split(":", 1)[1] if oe else "unknown"
    orgs[oid] = label[oe["source"]] if oe else "Organisation not stated"
    ui_edges.append({"person": label[e["source"]], "role": e["role"], "year": e.get("year"), "roleAsStated": e.get("role_as_stated"),
                     "production": label[e["target"]], "venue": oid, "url": e["url"], "evidence": e["sentence"], "rule": e["rule"],
                     "sha": e["sha256"][:12], "fetched": e["fetched_at"], "identity": e["identity"], "identityEvidence": e["identity_evidence"],
                     "producerRule": oe["rule"] if oe else None, "producerEvidence": oe["sentence"] if oe else None})
swept = max(p["fetched_at"] for p in pages)[:10]
data = json.dumps({"edges": ui_edges, "theatres": orgs, "swept": swept}, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
tpl = (ROOT.parent / "prototype/industry-intel.template.html").read_text()
(ROOT.parent / "prototype/industry-intel.html").write_text(tpl.replace("__DATA__", data))

# ---- TRACE.md ----
L = ["# Trace: how connections are made with no AI", "", "## Step 1. Source checks (check_sources.py)", ""]
for sid, r in sources.items():
    L.append("- **%s**: robots.txt HTTP %s, our agent allowed: %s%s" % (seed[sid]["name"], r["robots_status"], "yes" if r["our_agent_allowed"] else "no",
             "; blocks AI crawlers: " + ", ".join(r["ai_bots_blocked"]) if r["ai_bots_blocked"] else ""))
L += ["", "## Step 2. Fetch (fetch.py)", ""]
for sid in seed:
    ps = [p for p in pages if p["seed"] == sid]
    L.append("- %s: %d page(s): %s" % (seed[sid]["name"], len(ps), ", ".join(sorted({p["url"] for p in ps}))[:400]))
L += ["", "Note: burlesquethemusical.com redirects to burlesqueonstage.com; that site's own robots.txt was checked before reading it.", ""]

examples = [e for e in edges if e["type"] == "credit" and e["identity"] != "name match only"]
for i, e in enumerate(examples, 1):
    L += ["## Example %d: %s, %s on %s" % (i, label[e["source"]], e.get("role_as_stated", e["role"]).lower(), label[e["target"]]), "",
          "**Page:** %s  " % e["url"], "**Fetched:** %s · **SHA-256:** `%s`" % (e["fetched_at"], e["sha256"]), ""]
    for oe in org_edges[e["target"]]:
        if oe["url"] == e["url"] and oe.get("year") == e.get("year"):
            L += ["**Rule %s matched (%s):**" % (oe["rule"], oe["type"]), "", "> " + oe["sentence"], "",
                  "→ %s **%s** %s" % (label[oe["source"]], oe["type"], label[e["target"]]), ""]
    L += ["**Rule %s matched (credit):**" % e["rule"], "", "> " + e["sentence"], "",
          "→ %s **%s** on %s" % (label[e["source"]], e["role"].lower(), label[e["target"]]), "",
          "**Identity:** " + e["identity"] + (". Their own site says:" if e["identity_evidence"] else "."), ""]
    if e["identity_evidence"]:
        L += ["> " + e["identity_evidence"], ""]

creds = [e for e in edges if e["type"] == "credit"]
L += ["## Coverage", "",
      "- Productions: %d · People: %d · Organisations: %d" % tuple(sum(1 for n in nodes.values() if n["kind"] == k) for k in ("production", "person", "organisation")),
      "- Credits: %d (%d casting), of which %d have identity confirmed" % (len(creds), sum(1 for e in creds if e["role"] == "Casting director"), len(examples)),
      "- Producer pages with no production sentence the rules know: %d" % len(coverage["no_production"]),
      "- Producer pages where the title couldn't be read: %d" % len(coverage["title_unreadable"]),
      "- Official show-site pages with no credits written as text: %d" % len(coverage["official_site_no_credits"]),
      "", "Nothing is guessed: every page the rules couldn't read is listed in graph.json under `coverage`."]
(OUT / "TRACE.md").write_text("\n".join(L) + "\n")
print("productions=%d people=%d orgs=%d credits=%d with-identity=%d | coverage: %s" % (
    sum(1 for n in nodes.values() if n["kind"] == "production"), sum(1 for n in nodes.values() if n["kind"] == "person"),
    sum(1 for n in nodes.values() if n["kind"] == "organisation"), len(creds), len(examples), {k: len(v) for k, v in coverage.items()}))
