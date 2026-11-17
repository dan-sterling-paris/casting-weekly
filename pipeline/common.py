"""Shared, deterministic helpers for the no-AI pipeline (standard library only)."""
import hashlib
import json
import sys
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "catalogue"))
import re  # noqa: E402
from crawl import UA, get, html_to_text, read_sitemaps  # noqa: E402,F401

TERMS_RE = re.compile(r"terms|conditions|legal|website-use|terms-of-use|disclaimer", re.I)
CLAUSE_RE = re.compile(r"scrap|crawl|robot|spider|automated|data.?mining|harvest|extract|systematic|reproduc|republish|database", re.I)

CACHE = ROOT / "pages"   # saved page text, kept in the repo so patterns can be re-run without fetching
OUT = ROOT / "out"
AI_AGENTS = ["ClaudeBot", "anthropic-ai", "GPTBot", "CCBot", "Google-Extended", "Bytespider", "PerplexityBot", "Applebot-Extended"]


def seeds():
    return json.loads((ROOT / "seeds.json").read_text())["seeds"]


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def robots(base):
    """Return (parser or None, status code, raw text)."""
    st, body, _ = get(urljoin(base, "/robots.txt"))
    if st in (0, 401, 403):
        return None, st, ""
    text = body.decode("utf-8", "replace") if st == 200 else ""
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(text.splitlines())
    return rp, st, text


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def host(url):
    return urlparse(url).netloc.replace("www.", "")
