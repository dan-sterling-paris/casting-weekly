"""Step 5. Apply the rules to the fetched pages, confirm identities, and write:
  pipeline/out/graph.json   nodes and edges, every edge with its rule, sentence, URL, page hash and fetch time
  pipeline/out/TRACE.md     a step-by-step audit of the example and coverage counts
  prototype/industry-intel.html  the network view, built from graph.json
No AI anywhere: running it twice on the same pages gives identical output."""
import json
from collections import defaultdict
from common import CACHE, OUT, ROOT, seeds
from link import confirm, norm
from rules import credits, production

pages = [p for p in json.loads((OUT / "pages.json").read_text()) if p.get("status") == 200]
sources = {s["id"]: s for s in json.loads((OUT / "sources.json").read_text())}
seed = {s["id"]: s for s in seeds()}
text_of = {p["url"]: (CACHE / p["file"]).read_text() for p in pages}

# own-site text per person, for identity confirmation
own = defaultdict(str)
for p in pages:
    s = seed[p["seed"]]
    if s["kind"] == "person-site":
        own[norm(s["person"])] += "\n" + text_of[p["url"]]

nodes, edges, coverage = {}, [], {"no_production": [], "title_unreadable": [], "no_credits": []}
def node(nid, kind, label, **kw):
    nodes.setdefault(nid, {"id": nid, "kind": kind, "label": label, **kw})
    return nid

for p in sorted(pages, key=lambda x: x["url"]):
    s = seed[p["seed"]]
    if s["kind"] != "producer":
        continue
    t = text_of[p["url"]]
    prov = {"url": p["url"], "sha256": p["sha256"], "fetched_at": p["fetched_at"]}
    prod = production(t)
    if not prod:
        coverage["no_production"].append(p["url"]); continue
    rid, title, sent = prod
    if not title:
        coverage["title_unreadable"].append({"url": p["url"], "sentence": sent}); continue
    org = node("org:" + s["id"], "producer", s["name"], url=s["url"])
    pr = node("prod:" + norm(title), "production", title)
    if not any(e["source"] == org and e["target"] == pr for e in edges):
        edges.append({"source": org, "target": pr, "type": "produces", "rule": rid, "sentence": sent, **prov})
    cr = credits(t)
    if not cr:
        coverage["no_credits"].append(p["url"])
    for crid, role, name, csent in cr:
        pid = node("person:" + norm(name), "person", name)
        if any(e["source"] == pid and e["target"] == pr and e["role"] == role for e in edges if e["type"] == "credit"):
            continue
        conf = confirm(title, own.get(norm(name), ""))
        edges.append({"source": pid, "target": pr, "type": "credit", "role": role, "rule": crid, "sentence": csent,
                      "identity": "confirmed by own site" if conf else "name match only", "identity_evidence": conf, **prov})

graph = {"method": "pattern rules, no AI", "seeds": [s["id"] for s in seeds()],
         "nodes": sorted(nodes.values(), key=lambda n: n["id"]), "edges": edges, "coverage": coverage}
(OUT / "graph.json").write_text(json.dumps(graph, indent=1, ensure_ascii=False, sort_keys=True))

# ---- the network view (same data shape the console template reads) ----
label = {n["id"]: n["label"] for n in nodes.values()}
prod_org = {e["target"]: e for e in edges if e["type"] == "produces"}
ui_edges = []
for e in edges:
    if e["type"] != "credit":
        continue
    pe = prod_org[e["target"]]
    ui_edges.append({"person": label[e["source"]], "role": e["role"], "production": label[e["target"]],
                     "venue": pe["source"].split(":", 1)[1], "url": e["url"], "evidence": e["sentence"], "rule": e["rule"],
                     "sha": e["sha256"][:12], "fetched": e["fetched_at"], "identity": e["identity"], "identityEvidence": e["identity_evidence"],
                     "producerRule": pe["rule"], "producerEvidence": pe["sentence"], "producerUrl": pe["url"]})
swept = max(p["fetched_at"] for p in pages)[:10]
data = json.dumps({"edges": ui_edges, "theatres": {s["id"]: s["name"] for s in seeds()}, "swept": swept}, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
tpl = (ROOT.parent / "prototype/industry-intel.template.html").read_text()
(ROOT.parent / "prototype/industry-intel.html").write_text(tpl.replace("__DATA__", data))

# ---- TRACE.md: the worked example, step by step ----
ex = [e for e in edges if e["type"] == "credit" and e["identity"] == "confirmed by own site"]
L = ["# Trace: how one connection is made with no AI", ""]
src = sources["crossroads-live"]
L += ["## Step 1. Source check (check_sources.py)", "",
      "- Crossroads Live robots.txt: HTTP %s, our agent allowed: %s, `/press/` allowed: %s" % (src["robots_status"], src["our_agent_allowed"], src["allowed_paths"].get("/press/")),
      "- AI crawlers it blocks: " + ", ".join(src["ai_bots_blocked"]),
      "- Debbie O'Brien Casting robots.txt: HTTP %s, our agent allowed: %s" % (sources["debbie-obrien-casting"]["robots_status"], sources["debbie-obrien-casting"]["our_agent_allowed"]), ""]
n_cx = sum(1 for p in pages if p["seed"] == "crossroads-live")
L += ["## Step 2. Fetch (fetch.py)", "", "- Crossroads Live: %d press pages fetched from its own sitemap." % n_cx,
      "- Debbie O'Brien Casting: %d pages fetched." % sum(1 for p in pages if p["seed"] == "debbie-obrien-casting"), ""]
for i, e in enumerate(ex, 1):
    pe = prod_org[e["target"]]
    L += ["## Example %d: %s, %s on %s" % (i, label[e["source"]], e["role"].lower(), label[e["target"]]), "",
          "**Page:** %s  " % e["url"], "**Fetched:** %s · **SHA-256:** `%s`" % (e["fetched_at"], e["sha256"]), "",
          "**Step 3a. Rule %s (production) matched:**" % pe["rule"], "", "> " + pe["sentence"], "",
          "→ connection: Crossroads Live **produces** %s" % label[e["target"]], "",
          "**Step 3b. Rule %s (credit) matched:**" % e["rule"], "", "> " + e["sentence"], "",
          "→ connection: %s **%s** on %s" % (label[e["source"]], e["role"].lower(), label[e["target"]]), "",
          "**Step 4. Identity:** %s. Her own site (debbieobrien.net) says:" % e["identity"], "", "> " + (e["identity_evidence"] or ""), ""]
creds = [e for e in edges if e["type"] == "credit"]
L += ["## Whole archive", "",
      "- Productions found: %d" % sum(1 for n in nodes.values() if n["kind"] == "production"),
      "- People found: %d" % sum(1 for n in nodes.values() if n["kind"] == "person"),
      "- Credits found: %d (%d casting)" % (len(creds), sum(1 for e in creds if e["role"] == "Casting director")),
      "- Pages with no Crossroads Live production sentence: %d" % len(coverage["no_production"]),
      "- Pages where a production sentence was found but no title could be read: %d" % len(coverage["title_unreadable"]),
      "- Pages with a production but no credit matched: %d" % len(coverage["no_credits"]), "",
      "Nothing is guessed: pages the rules can't read are listed in graph.json under `coverage`, so a person can see what was missed."]
(OUT / "TRACE.md").write_text("\n".join(L) + "\n")
print("productions=%d people=%d credits=%d confirmed=%d | no_production=%d title_unreadable=%d no_credits=%d" % (
    sum(1 for n in nodes.values() if n["kind"] == "production"), sum(1 for n in nodes.values() if n["kind"] == "person"),
    len(creds), len(ex), len(coverage["no_production"]), len(coverage["title_unreadable"]), len(coverage["no_credits"])))
