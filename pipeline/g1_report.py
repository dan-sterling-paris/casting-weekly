"""Test rule G1 on every saved page: what it reads, per site, and which pages it skips as mixed. No fetching, no AI."""
import json
from collections import Counter, defaultdict
from common import CACHE, OUT
from rules import credits, label_pairs

pages = [p for p in json.loads((OUT / "pages.json").read_text()) if p.get("status") == 200]
seen, by_site, status = set(), defaultdict(list), Counter()
for p in pages:
    if p["file"] in seen:
        continue
    seen.add(p["file"])
    t = (CACHE / p["file"]).read_text()
    found, st = label_pairs(t)
    status[st] += 1
    sentence = {(r, n) for _, r, n, _ in credits(t)}
    for rid, role, name, ev in found:
        by_site[p["seed"]].append((p["url"], role, name, ev, (role, name) in sentence))
print("pages tested: %d distinct · status: %s" % (len(seen), dict(status)))
for site, rows in by_site.items():
    new = [r for r in rows if not r[4]]
    print("\n== %s: %d G1 credits (%d not found by the sentence rules)" % (site, len(rows), len(new)))
    for url, role, name, ev, dup in rows[:40]:
        print("  %s %-16s %-26s | %s | %s" % ("  " if dup else "+ ", role, name, ev[:70], url.split("/")[-1][:50]))
