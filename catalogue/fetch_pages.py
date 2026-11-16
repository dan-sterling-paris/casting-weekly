"""Fetch specific pages politely (robots.txt obeyed, identified, rate-limited) and save their text.

Usage: python3 catalogue/fetch_pages.py OUT_DIR URL [URL ...]
Prints one line per URL: status, robots decision, saved file. Text goes to OUT_DIR (keep it out of git).
"""
import hashlib
import sys
import urllib.robotparser
from pathlib import Path
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(Path(__file__).parent))
from crawl import UA, get, html_to_text  # noqa: E402

_robots = {}


def allowed(url):
    base = "%s://%s" % (urlparse(url).scheme, urlparse(url).netloc)
    if base not in _robots:
        st, body, _ = get(urljoin(base, "/robots.txt"))
        rp = urllib.robotparser.RobotFileParser()
        if st in (401, 403) or st == 0:
            _robots[base] = None
        else:
            rp.parse(body.decode("utf-8", "replace").splitlines() if st == 200 else [])
            _robots[base] = rp
    rp = _robots[base]
    return rp is not None and rp.can_fetch(UA, url)


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for url in sys.argv[2:]:
        if not allowed(url):
            print("SKIP robots  ", url)
            continue
        st, body, final = get(url)
        if st != 200:
            print("FAIL %-8s" % st, url)
            continue
        title, text = html_to_text(body)
        name = urlparse(final).netloc.replace("www.", "").split(".")[0] + "-" + hashlib.sha256(text.encode()).hexdigest()[:10] + ".txt"
        (out / name).write_text("URL: %s\nTITLE: %s\n\n%s\n" % (final, title, text))
        print("OK   %6d ch" % len(text), name, final)


if __name__ == "__main__":
    main()
