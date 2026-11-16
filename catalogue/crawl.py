"""Casting Weekly catalogue crawler. Python standard library only.

Reads each theatre's own website politely:
  * obeys robots.txt (401/403 on robots.txt means the whole site is off-limits);
  * identifies itself and waits between requests;
  * finds what's-on, production and announcement pages from the site's own sitemap,
    preferring the most recently updated ones;
  * saves plain page text to catalogue/cache/<date>/ (never committed).

Usage:  python3 catalogue/crawl.py catalogue/sources.json
"""
import gzip
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

UA = "CastingWeeklyBot/0.2 (+https://castingweekly.com/bot; office@castingweekly.com)"
DELAY = 2.0
TIMEOUT = 25
MAX_SITEMAPS = 10
MAX_EVENT_PAGES = 9
MAX_NEWS_PAGES = 4

EVENT_RE = re.compile(r"/(whats-on|what-s-on|whatson|events?|shows?|productions?|performances?)/[^/]+/?$", re.I)
NEWS_RE = re.compile(r"/(news|press|blog|stories|articles?)/.*(announce|season|programme|program|cast|new-production|2027)", re.I)
SKIP_RE = re.compile(r"\.(pdf|jpe?g|png|gif|docx?|mp[34]|xml)$|\?|/(tag|category|page)/|workshop|class|course|tour-of|venue-hire|gift|membership|youth|community|academy|access", re.I)

_last = {}


def get(url):
    host = urlparse(url).netloc
    wait = DELAY - (time.time() - _last.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _last[host] = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read(5_000_000)
            if body[:2] == b"\x1f\x8b":
                body = gzip.decompress(body)
            return r.status, body, r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, b"", url
    except Exception as e:
        return 0, str(e).encode(), url


class TextExtractor(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template", "iframe", "nav", "footer"}
    BLOCK = {"p", "div", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "td", "th", "section",
             "article", "header", "ul", "ol", "table", "dt", "dd", "blockquote", "time", "span"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.title, self._t = [], 0, "", False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        if tag in self.BLOCK and tag != "span":
            self.out.append("\n")
        if tag == "title":
            self._t = True

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in self.BLOCK and tag != "span":
            self.out.append("\n")
        if tag == "title":
            self._t = False

    def handle_data(self, data):
        if self._t:
            self.title += data
        elif not self.skip:
            self.out.append(data)

    def text(self):
        t = re.sub(r"[ \t\r\f\v ]+", " ", "".join(self.out))
        lines = [ln.strip() for ln in t.splitlines()]
        return "\n".join(ln for ln in lines if ln)


def html_to_text(body):
    p = TextExtractor()
    p.feed(body.decode("utf-8", "replace"))
    return p.title.strip(), p.text()


def read_sitemaps(base, rp):
    maps = list(rp.site_maps() or []) or [urljoin(base, "/sitemap.xml")]
    seen, urls, n = set(), [], 0
    while maps and n < MAX_SITEMAPS:
        sm = maps.pop(0)
        if sm in seen or not rp.can_fetch(UA, sm):
            continue
        seen.add(sm)
        st, body, _ = get(sm)
        n += 1
        if st != 200:
            continue
        xml = body.decode("utf-8", "replace")
        if "<sitemapindex" in xml[:3000]:
            locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)
            # event / show / news sitemaps first
            maps.extend(sorted(locs, key=lambda u: (not re.search(r"event|show|production|whats|news|post|page", u, re.I), u)))
            continue
        for block in re.findall(r"<url>(.*?)</url>", xml, re.S):
            loc = re.search(r"<loc>\s*([^<\s]+)\s*</loc>", block)
            lm = re.search(r"<lastmod>\s*([^<\s]+)\s*</lastmod>", block)
            if loc:
                urls.append((loc.group(1), lm.group(1)[:10] if lm else ""))
    return urls, n


def crawl(src, cache):
    base = src["url"].rstrip("/") + "/"
    rec = {"id": src["id"], "name": src["name"], "base": base, "pages": []}
    st, body, _ = get(urljoin(base, "/robots.txt"))
    rp = urllib.robotparser.RobotFileParser()
    if st in (401, 403) or st == 0:
        rec["robots"] = "blocked or unreachable (%s)" % st
        return rec
    rp.parse(body.decode("utf-8", "replace").splitlines() if st == 200 else [])
    rec["robots"] = "found" if st == 200 else "none"
    urls, n = read_sitemaps(base, rp)
    rec["sitemaps_read"], rec["sitemap_urls"] = n, len(urls)
    host = urlparse(base).netloc.replace("www.", "")
    urls = [(u, lm) for u, lm in dict(urls).items() if urlparse(u).netloc.replace("www.", "") == host and not SKIP_RE.search(u)]
    events = sorted([x for x in urls if EVENT_RE.search(urlparse(x[0]).path)], key=lambda x: x[1], reverse=True)[:MAX_EVENT_PAGES]
    news = sorted([x for x in urls if NEWS_RE.search(urlparse(x[0]).path)], key=lambda x: x[1], reverse=True)[:MAX_NEWS_PAGES]
    for u, lm in events + news:
        if not rp.can_fetch(UA, u):
            rec["pages"].append({"url": u, "status": "disallowed by robots.txt"})
            continue
        st, pb, final = get(u)
        item = {"url": final, "status": st, "lastmod": lm}
        if st == 200:
            title, text = html_to_text(pb)
            h = hashlib.sha256(text.encode()).hexdigest()
            f = cache / ("%s-%s.txt" % (src["id"], h[:10]))
            f.write_text("URL: %s\nTITLE: %s\n\n%s\n" % (final, title, text))
            item.update(title=title, cache=str(f), sha256=h, chars=len(text))
        rec["pages"].append(item)
    return rec


def main():
    sources = json.loads(Path(sys.argv[1]).read_text())["sources"]
    today = date.today().isoformat()
    out = Path("catalogue/runs") / today
    cache = Path("catalogue/cache") / today
    out.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    results = []
    for s in sources:
        r = crawl(s, cache)
        results.append(r)
        ok = sum(1 for p in r["pages"] if p.get("status") == 200)
        print("%-20s robots=%-8s sitemap_urls=%-6s pages=%d" % (s["id"], r.get("robots"), r.get("sitemap_urls", "-"), ok), flush=True)
        (out / "crawl.json").write_text(json.dumps({"date": today, "ua": UA, "sites": results}, indent=1))
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
