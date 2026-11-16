"""Crawl theatres' own production pages (past and present) for credits. Standard library only.

Same politeness as crawl.py (robots.txt obeyed, identified, 2 seconds between requests to a site),
with sites crawled side by side so the whole sample finishes in a few minutes.

Usage: python3 catalogue/crawl_credits.py catalogue/sources.json [PAGES_PER_SITE]
Page text goes to catalogue/cache/credits/ (never committed); a summary to catalogue/runs/credits/crawl.json.
"""
import hashlib
import json
import re
import sys
import threading
import urllib.robotparser
from pathlib import Path
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(Path(__file__).parent))
from crawl import UA, get, html_to_text, read_sitemaps  # noqa: E402

PROD_RE = re.compile(r"/(whats-on|what-s-on|whatson|events?|shows?|productions?|past-productions?|archive|news)/[^/]+/?$", re.I)
SKIP_RE = re.compile(r"\.(pdf|jpe?g|png|gif|docx?|mp[34]|xml)$|\?|/(tag|category|page)/|youth|class|course|workshop|term|taster|"
                     r"gift|membership|venue-hire|dining|dinner|tour-of|exhibition|screening|film|cinema|concert|comedy|"
                     r"family-saturdays|bridges|social-theatre|access|vacanc|job", re.I)
NEWS_KEEP = re.compile(r"cast|creative|announce|season|production", re.I)
OUT = Path("catalogue/cache/credits")
RUNS = Path("catalogue/runs/credits")


def pick(urls, n):
    keep = []
    for u, lm in urls:
        path = urlparse(u).path
        if SKIP_RE.search(u) or not PROD_RE.search(path):
            continue
        if "/news/" in path and not NEWS_KEEP.search(path):
            continue
        keep.append((u, lm))
    keep.sort(key=lambda x: x[1], reverse=True)   # newest first, then older ones fill the budget
    return keep[:n]


def crawl_site(src, n, results):
    base = src["url"].rstrip("/") + "/"
    rec = {"id": src["id"], "name": src["name"], "pages": 0, "skipped_robots": 0, "errors": 0}
    st, body, _ = get(urljoin(base, "/robots.txt"))
    if st in (0, 401, 403):
        rec["robots"] = "blocked or unreachable"
        results.append(rec)
        return
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(body.decode("utf-8", "replace").splitlines() if st == 200 else [])
    urls, _ = read_sitemaps(base, rp)
    host = urlparse(base).netloc.replace("www.", "")
    urls = [(u, lm) for u, lm in dict(urls).items() if urlparse(u).netloc.replace("www.", "") == host]
    for u, _ in pick(urls, n):
        if not rp.can_fetch(UA, u):
            rec["skipped_robots"] += 1
            continue
        st, pb, final = get(u)
        if st != 200:
            rec["errors"] += 1
            continue
        title, text = html_to_text(pb)
        f = OUT / ("%s-%s.txt" % (src["id"], hashlib.sha256(text.encode()).hexdigest()[:10]))
        f.write_text("URL: %s\nTITLE: %s\n\n%s\n" % (final, title, text))
        rec["pages"] += 1
    print("%-22s pages=%d skipped_robots=%d errors=%d" % (src["id"], rec["pages"], rec["skipped_robots"], rec["errors"]), flush=True)
    results.append(rec)


def main():
    sources = json.loads(Path(sys.argv[1]).read_text())["sources"]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    OUT.mkdir(parents=True, exist_ok=True)
    RUNS.mkdir(parents=True, exist_ok=True)
    results = []
    threads = [threading.Thread(target=crawl_site, args=(s, n, results)) for s in sources]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    (RUNS / "crawl.json").write_text(json.dumps({"ua": UA, "pages_per_site": n, "sites": results}, indent=1))
    print("DONE", sum(r["pages"] for r in results), "pages")


if __name__ == "__main__":
    main()
