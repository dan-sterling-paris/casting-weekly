"""Read every saved page (pipeline/pages/), apply the three patterns, write the network. No fetching, no AI.

  python3 pipeline/extract.py

Writes pipeline/out/graph.json, pipeline/out/NOT_READ.md and prototype/industry-intel.html.
"""
import json
import re
from collections import defaultdict
from common import CACHE, OUT, ROOT, key, seeds
from rules import label_pairs, pattern_b, pattern_s, show_of_page


SMALL = {"a", "an", "and", "at", "by", "for", "in", "of", "on", "or", "the", "to", "with"}


def title_case(t):
    """Display a title written IN CAPITALS in normal capitals; keep short words in brackets as written (e.g. RSC)."""
    if t != t.upper():
        return t
    out = []
    for i, w in enumerate(t.split()):
        core = w.strip("()[]:,.!?'’\"")
        if w.startswith("(") and len(core) <= 4:
            out.append(w)
        elif i > 0 and core.lower() in SMALL:
            out.append(w.lower())
        else:
            out.append(re.sub(r"[A-Za-z][A-Za-z'’]*", lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(), w))
    return " ".join(out)


def owner_from_title(page_title):
    t = re.split(r" [-|–—] ", page_title)[0]
    return re.sub(r"(\s+(CDG|CSA))+$", "", t.strip())


site_name = {s["id"]: s["name"] for s in seeds()}
pages = [p for p in json.loads((OUT / "pages.json").read_text()) if p.get("status") == 200]
edges, shows, not_read, seen = [], {}, defaultdict(list), set()


people = {}


def add(person, role, show, org, rule, evidence, url, year=None):
    person = people.setdefault(key(person), person.replace("’", "'"))
    k = (key(person), role, key(show), year)
    if k in seen:
        return
    seen.add(k)
    shows.setdefault(key(show), title_case(show))
    edges.append({"person": person, "role": role, "production": shows[key(show)], "venue": org, "url": url,
                  "evidence": evidence, "rule": rule, "year": year})


for p in sorted(pages, key=lambda x: x["url"]):
    text = (CACHE / p["file"]).read_text().split("\n\n", 1)[-1]   # page text only, without the saved URL/TITLE header
    site = site_name.get(p["seed"], p["seed"])
    # B: credit blocks on a person's CV page
    owner = owner_from_title(p.get("title", ""))
    blocks = pattern_b(text, owner)
    for b in blocks:
        add(owner, "Casting director", b["title"], b["venue"] or "Venue not stated", "B", b["evidence"], p["url"], b["year"])
        for d in b["directors"]:
            add(d, "Director", b["title"], b["venue"] or "Venue not stated", "B", b["evidence"], p["url"], b["year"])
    # S and L: credits written in sentences or as label/name lines
    found = pattern_s(text)
    lab, status = label_pairs(text)
    found += [c for c in lab if (c[1], c[2].lower()) not in {(r, n.lower()) for _, r, n, _ in found}]
    if found:
        # a person's CV page (it has credit blocks) is about the person, so its heading is never a show
        show, why = show_of_page(text, [site], "" if blocks else p.get("title", ""), p["url"])
        if not show:
            not_read["Credits found, but the page doesn't say which show"].append(p["url"])
        else:
            for rule, role, name, ev in found:
                add(name, role, show, site, rule, ev, p["url"])
    elif not blocks:
        not_read["No credits in a pattern we read"].append(p["url"])
    if status == "mixed":
        not_read["Label/name lines in both orders (skipped)"].append(p["url"])

# K: credits found by the production-credits-lookup skill and confirmed on the cited page by check_lookups.py
lookup_file = OUT / "lookup_credits.json"
lookups = json.loads(lookup_file.read_text()) if lookup_file.exists() else []
before = len(edges)
for c in lookups:
    add(c["person"], c["role"], c["production"], c["venue"], "K", c["evidence"], c["url"])
from_lookups = len(edges) - before

swept = max(p["fetched_at"] for p in pages)[:10]
graph = {"method": "scrape -> text -> patterns S, L, B; no AI" + ("; plus K: skill lookups checked on the page by script" if from_lookups else ""), "edges": edges, "not_read": not_read}
(OUT / "graph.json").write_text(json.dumps(graph, indent=1, ensure_ascii=False, sort_keys=True))
md = ["# Pages not read", "", "These pages were fetched but nothing on them matched a pattern. Nothing was guessed.", ""]
for why, urls in not_read.items():
    md += ["## %s (%d)" % (why, len(urls)), ""] + ["- " + u for u in urls] + [""]
(OUT / "NOT_READ.md").write_text("\n".join(md))

orgs = {e["venue"]: e["venue"] for e in edges}
data = json.dumps({"edges": edges, "theatres": orgs, "swept": swept}, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
tpl = (ROOT.parent / "prototype/industry-intel.template.html").read_text()
(ROOT.parent / "prototype/industry-intel.html").write_text(tpl.replace("__DATA__", data))

cd = defaultdict(int)
for e in edges:
    if e["role"] == "Casting director":
        cd[e["person"]] += 1
print("pages %d · credits %d · shows %d · people %d · casting directors: %s" % (
    len(pages), len(edges), len(shows), len({key(e["person"]) for e in edges}), dict(sorted(cd.items(), key=lambda x: -x[1]))))
print("from checked lookups (K): %d" % from_lookups)
print("not read:", {k: len(v) for k, v in not_read.items()})
