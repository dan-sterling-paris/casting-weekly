"""Read one page's HTML: production name from the SEO tags, people from the plain text with regular expressions.

No CSS selectors or XPath are used for names. The page is stripped to plain text with
BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True) and every name comes from a regex on that text.

    from seo_extract import extract
    extract(html)  ->  {"production", "director", "writer", "casting_director"}  or  {"error": "..."}
"""
import re
from bs4 import BeautifulSoup

# 2-3 capitalised words, e.g. "Jamie Lloyd", "Stuart Burt CDG" is cut to "Stuart Burt" by the stop list.
# Role words are not part of a name, so "Directed by Jamie Lloyd Casting by ..." gives "Jamie Lloyd".
STOP = r"(?!(?i:Casting|Cast|Director|Directed|Dir|Written|Writer|Writers|Music|Lyrics|Book|Design|Designer|Lighting|Sound|"
STOP += r"Choreography|Choreographer|Producer|Produced|And|With|By|The|CDG|CSA)\b)"
WORD = STOP + r"[A-Z][A-Za-z'’\-]+"
NAME = r"(" + WORD + r"(?:\s+" + WORD + r"){1,2})"

# Labels are case-insensitive; the name itself must be capitalised.
DIRECTOR = re.compile(r"(?<![A-Za-z])(?<!Casting )(?<!CASTING )(?i:directed\s+by|director|dir\.?)(?![A-Za-z])\s*[:\-–]?\s*" + NAME)
WRITER = re.compile(r"(?<![A-Za-z])(?i:written\s+by|writer)(?![A-Za-z])\s*[:\-–]?\s*" + NAME)
CASTING = re.compile(r"(?<![A-Za-z])(?i:casting\s+by)(?![A-Za-z])\s*[:\-–]?\s*" + NAME)


def _norm(s):
    return re.sub(r"\s+", " ", s).strip().casefold()


def _unique(names):
    out = {}
    for n in names:
        out.setdefault(_norm(n), n)
    return list(out.values())


def extract(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Production name from the page's SEO metadata
    og = soup.find("meta", attrs={"property": "og:title"})
    og_title = (og.get("content") or "").strip() if og else ""
    title_tag = soup.title.get_text(strip=True) if soup.title else ""
    production = og_title or re.split(r"\s+[-–—]\s+", title_tag)[0].strip()
    if not production:
        return {"error": "No og:title or <title> on the page"}

    # Plain text. The <title> is removed so it can't count as the "other" appearance in Rule 1;
    # scripts and styles are removed because they are code, not page text.
    for t in soup(["title", "script", "style", "noscript"]):
        t.decompose()
    text = soup.get_text(separator=" ", strip=True)

    # Rule 1: the name is in <title> or og:title (case-insensitive) and appears again in the body text
    if _norm(production) not in _norm(og_title) and _norm(production) not in _norm(title_tag):
        return {"error": "Title did not appear in the title tags"}
    if _norm(production) not in _norm(text):
        return {"error": "Title did not appear in the body text"}

    directors = _unique(DIRECTOR.findall(text))
    writers = _unique(WRITER.findall(text))
    casting = _unique(CASTING.findall(text))

    # Rule 2: one casting director per page (the same name repeated is fine)
    if len(casting) > 1:
        return {"error": "Multiple distinct casting directors found"}

    return {"production": production, "director": directors, "writer": writers,
            "casting_director": casting[0] if casting else None}
