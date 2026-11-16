"""Step 2. Fetch every allowed page under each seed's read paths, found from the site's own sitemap.
Saves page text to pipeline/cache/ and a manifest (URL, time, hash) to pipeline/out/pages.json. No AI involved."""
import json
from urllib.parse import urlparse
from common import CACHE, OUT, UA, get, host, html_to_text, now, read_sitemaps, robots, seeds, sha

CACHE.mkdir(exist_ok=True)
manifest = []
for s in seeds():
    base = s["url"].rstrip("/") + "/"
    rp, st, _ = robots(base)
    if not rp:
        print("blocked", s["id"]); continue
    urls, _ = read_sitemaps(base, rp)
    wanted = sorted({u for u, _ in urls if host(u) == host(base) and any(urlparse(u).path.startswith(p) for p in s["read"])
                     and urlparse(u).path.rstrip("/") not in [p.rstrip("/") for p in s["read"] if p != "/"]})
    must = [u for u in s.get("must_include", []) if u in wanted or True]
    wanted = (must + [u for u in wanted if u not in must])[: s.get("max_pages", len(wanted))]
    got = 0
    for u in wanted:
        if not rp.can_fetch(UA, u):
            manifest.append({"seed": s["id"], "url": u, "status": "disallowed by robots.txt"}); continue
        code, body, final = get(u)
        rec = {"seed": s["id"], "url": final, "status": code, "fetched_at": now()}
        if code == 200:
            title, text = html_to_text(body)
            h = sha(text)
            (CACHE / (h[:16] + ".txt")).write_text("URL: %s\nTITLE: %s\n\n%s\n" % (final, title, text))
            rec.update(title=title, sha256=h, file=h[:16] + ".txt"); got += 1
        manifest.append(rec)
    print("%-24s sitemap urls=%d wanted=%d fetched=%d" % (s["id"], len(urls), len(wanted), got), flush=True)
OUT.mkdir(exist_ok=True)
(OUT / "pages.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
