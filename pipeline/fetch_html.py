"""Fetch the raw HTML for a sample of already-listed pages, politely (robots.txt, 2 s per site). Saves pipeline/html/<id>.html.

  python3 pipeline/fetch_html.py 20
"""
import json
import sys
from urllib.parse import urlparse
from common import OUT, ROOT, UA, get, robots

n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
pages = [p for p in json.loads((OUT / "pages.json").read_text()) if p.get("status") == 200]
by_seed = {}
for p in pages:
    by_seed.setdefault(p["seed"], []).append(p)
sample = []
while len(sample) < n and any(by_seed.values()):     # take pages from each source in turn
    for s in list(by_seed):
        if by_seed[s] and len(sample) < n:
            sample.append(by_seed[s].pop(0))
HTML = ROOT / "html"
HTML.mkdir(exist_ok=True)
rules = {}
for p in sample:
    site = "%s://%s" % (urlparse(p["url"]).scheme, urlparse(p["url"]).netloc)
    if site not in rules:
        rules[site] = robots(site)[0]
    if rules[site] is None or not rules[site].can_fetch(UA, p["url"]):
        print("robots.txt says no:", p["url"]); continue
    st, body, final = get(p["url"])
    if st == 200:
        (HTML / p["file"].replace(".txt", ".html")).write_bytes(body)
    print(st, p["url"])
