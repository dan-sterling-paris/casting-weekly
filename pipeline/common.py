"""Shared helpers: polite fetching (robots.txt, 2 s per site), page text, name matching. Standard library only."""
import gzip
import hashlib
import re
import time
import unicodedata
import urllib.error
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "pages"   # text of every cited page, kept so the check never refetches a page
OUT = ROOT / "out"
UA = "CastingWeeklyBot/0.2 (+https://castingweekly.com/bot; office@castingweekly.com)"
DELAY, TIMEOUT = 2.0, 25
_last = {}


def get(url):
    """Fetch politely: identify ourselves and wait DELAY seconds between requests to the same site."""
    site = urlparse(url).netloc
    wait = DELAY - (time.time() - _last.get(site, 0))
    if wait > 0:
        time.sleep(wait)
    _last[site] = time.time()
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


def robots(base):
    """Return (parser or None, status code, raw text). 401/403/unreachable robots.txt means the site is off-limits."""
    st, body, _ = get(urljoin(base, "/robots.txt"))
    if st in (0, 401, 403):
        return None, st, ""
    text = body.decode("utf-8", "replace") if st == 200 else ""
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(text.splitlines())
    return rp, st, text


class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template", "iframe", "nav", "footer"}
    BLOCK = {"p", "div", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "td", "th", "section",
             "article", "header", "ul", "ol", "table", "dt", "dd", "blockquote", "time"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.title, self._t = [], 0, "", False

    def handle_starttag(self, tag, attrs):
        self.skip += tag in self.SKIP
        if tag in self.BLOCK:
            self.out.append("\n")
        self._t = self._t or tag == "title"

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in self.BLOCK:
            self.out.append("\n")
        if tag == "title":
            self._t = False

    def handle_data(self, data):
        if self._t:
            self.title += data
        elif not self.skip:
            self.out.append(data)


def html_to_text(body):
    """(page title, page text with one block per line)."""
    p = _Text()
    p.feed(body.decode("utf-8", "replace"))
    t = re.sub(r"[ \t\r\f\v ]+", " ", "".join(p.out))
    return p.title.strip(), "\n".join(ln.strip() for ln in t.splitlines() if ln.strip())


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def key(s):
    """Compare names and titles ignoring case, punctuation, curly apostrophes, a leading "The" and a trailing "the musical"."""
    s = unicodedata.normalize("NFKC", s).replace("’", "'").casefold()
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return re.sub(r"^the |( the)? musical$", "", s).strip()
