"""Test sample: the newest 5 review pages from each review site Dan picked, found from each site's own sitemap.
Polite: robots.txt checked per URL, 2 s per site. Saves raw HTML to pipeline/html_reviews/ (not committed).

  python3 fetch_reviews.py
"""
import json
import re
from urllib.parse import urlparse
from common import ROOT, UA, get, robots, sha

SITES = {   # site -> sitemap that lists its reviews
    "WhatsOnStage": "https://www.whatsonstage.com/news-sitemap59.xml",
    "Everything Theatre": "https://everything-theatre.co.uk/newssitemap.xml",
    "LondonTheatre1": "https://www.londontheatre1.com/post-sitemap15.xml",
    "West End Best Friend": "https://www.westendbestfriend.co.uk/sitemap.xml",
}
PER_SITE = 5
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?\s*([^<\s\]]+)")
LASTMOD = re.compile(r"<lastmod>\s*([^<\s]+)")

out = ROOT / "html_reviews"
out.mkdir(exist_ok=True)
manifest = []
for name, sm in SITES.items():
    site = "%s://%s/" % (urlparse(sm).scheme, urlparse(sm).netloc)
    rp = robots(site)[0]
    st, body, _ = get(sm)
    rows = []
    for i, b in enumerate(re.findall(r"<url>(.*?)</url>", body.decode("utf-8", "replace"), re.S)):
        loc, lm = LOC.search(b), LASTMOD.search(b)
        if loc and "review" in loc.group(1):
            num = re.search(r"_(\d+)/?$", loc.group(1))
            rows.append((lm.group(1)[:10] if lm else "", int(num.group(1)) if num else 0, -i, loc.group(1)))
    rows.sort(reverse=True)   # newest first: lastmod, else the site's article number, else sitemap order
    for *_, url in rows[:PER_SITE]:
        if not (rp and rp.can_fetch(UA, url)):
            print("robots.txt says no:", url); continue
        st, body, final = get(url)
        f = sha(url)[:16] + ".html"
        if st == 200:
            (out / f).write_bytes(body)
        manifest.append({"site": name, "url": url, "status": st, "file": f})
        print(st, name, url)
(out / "manifest.json").write_text(json.dumps(manifest, indent=1))
