"""Check the production-credits-lookup skill's answers with no AI, before they reach the graph.

The skill (Claude) finds credits and the pages that state them; it saves its JSON, untouched, in pipeline/lookups/.
This script opens every cited page itself (robots.txt obeyed, 2 s per site) and keeps a credit only if that page's
text contains both the person's name and the production's name. Everything else is listed with the reason.

  python3 pipeline/check_lookups.py        then        python3 pipeline/extract.py

Writes pipeline/out/lookup_credits.json (kept) and pipeline/out/unconfirmed.json (not kept, with the reason; shown on
the site's Data quality page).
"""
import json
import re
from collections import defaultdict
from urllib.parse import urlparse
from common import CACHE, OUT, ROOT, UA, get, html_to_text, key, now, robots, sha

# a role word with one of these in front is a different job ("Associate Director", "Musical Director")
QUALIFIERS = (r"(Associate|Assistant|Resident|Fight|Intimacy|Movement|Musical|Music|Artistic|Video|Lighting|Sound|Co-|Deputy|"
              r"Executive|Creative|Production|Technical|Puppetry|Voice|Dialect|Children's|Children’s|Revival)")


def sentences(text):
    out = []
    for line in text.split("\n"):
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", line):
            if len(s.strip()) > 3:
                out.append(s.strip())
    return out

LOOKUPS = ROOT / "lookups"
PAGES = OUT / "lookup_pages.json"
SKIP = {"", "unknown"}
WRITER_PART = {"book": "Writer", "music": "Composer", "lyrics": "Lyricist", "music and lyrics": "Composer",
               "music & lyrics": "Composer", "additional lyrics": "Lyricist", "adapted by": "Writer", "written by": "Writer", "playwright": "Writer"}

# the role must be stated next to the name: in the same sentence, or on the line just before or after it
ROLE_WORD = {"Casting director": r"casting", "Director": r"direct", "Writer": r"writ|book|creat|playwright|adapt|monologue|script",
             "Composer": r"music\b|compos|score", "Lyricist": r"lyric"}


def around(sentence, name, width=180):
    """A long sentence is shortened to the part around the name, so the quote always shows it."""
    if len(sentence) <= 2 * width:
        return sentence
    m = re.search(r"[\W_]+".join(re.escape(w) for w in re.findall(r"[A-Za-z0-9]+", name)), sentence, re.I)
    if not m:
        return sentence[:2 * width] + "…"
    a, b = max(0, m.start() - width), min(len(sentence), m.end() + width)
    return ("…" if a else "") + sentence[a:b] + ("…" if b < len(sentence) else "")


LABEL_WORDS = re.compile(r"\b(casting|castings|director|directed|direction|music|lyrics|book|written|writer|bookwriter|composer|"
                         r"lyricist|original|adaptation|adapted|creative|team|by|and|uk)\b", re.I)


def is_label(line, role):
    """A line that only names a role, e.g. "Director -", "Music & Lyrics by", "UK Casting" (not "Associate Director")."""
    if len(line) >= 60 or not re.search(r"\b(?:%s)" % ROLE_WORD[role], line, re.I):
        return False
    if role in ("Director", "Casting director") and re.search(r"\b%s" % QUALIFIERS, line):
        return False
    rest = LABEL_WORDS.sub(" ", line)
    return not re.search(r"[A-Z][a-z'’-]+\s+[A-Z][a-z]", rest)   # no other person's name on the label line


def role_evidence(text, name, role):
    """Prefer a credit label line next to the name ("Director -" / "Joe Mantello"); otherwise a sentence with both."""
    rx = re.compile(r"\b(?:%s)" % ROLE_WORD[role], re.I)
    lines = [x.strip() for x in text.split("\n")]
    for i, line in enumerate(lines):
        if contains(line, name) and len(line) < 80:   # a short label/name line
            for j in (i - 1, i + 1):
                if 0 <= j < len(lines) and is_label(lines[j], role):
                    return " / ".join([lines[j], line] if j < i else [line, lines[j]])
    for s in sentences(text):
        if contains(s, name) and rx.search(s):
            return s
    return None


pages = json.loads(PAGES.read_text()) if PAGES.exists() else {}
rules_for = {}


def page_text(url):
    """Fetch a cited page once (politely) and keep its text in pipeline/pages/, like every other page we read."""
    if url not in pages:
        u = urlparse(url)
        site = "%s://%s/" % (u.scheme, u.netloc)
        if site not in rules_for:
            rules_for[site] = robots(site)[0]
        rp = rules_for[site]
        if rp is None or not rp.can_fetch(UA, url):
            pages[url] = {"status": "blocked by robots.txt"}
        else:
            st, body, final = get(url)
            rec = {"status": st, "fetched_at": now(), "final": final}
            if st == 200:
                title, text = html_to_text(body)
                f = sha(text)[:16] + ".txt"
                (CACHE / f).write_text("URL: %s\nTITLE: %s\n\n%s\n" % (final, title, text))
                rec.update(title=title, file=f)
            pages[url] = rec
    rec = pages[url]
    if rec.get("file"):
        return (CACHE / rec["file"]).read_text().split("\n\n", 1)[-1], None
    return None, "page could not be read (%s)" % rec["status"]


def contains(text, phrase):
    return (" %s " % key(phrase)) in (" %s " % key(text))


def people(field, value):
    """'A; B' -> [(role, name)]. Writer parts like 'Book: X; Music: Y' keep their own roles."""
    role = {"Casting Director": "Casting director", "Director": "Director", "Writer": "Writer"}[field]
    out = []
    for part in value.split(";"):
        part, r = part.strip(), role
        m = re.match(r"^([A-Za-z &]+?)\s*:\s*(.+)$", part)
        if field == "Writer" and m:
            r, part = WRITER_PART.get(m.group(1).strip().lower(), "Writer"), m.group(2)
        part = re.sub(r"\s+from the (?:novel|play|film|book|story).*$", "", part, flags=re.I)   # keep the adapter only
        part = re.sub(r"^(?:adapted|written|book|music|lyrics)(?: and lyrics)? by\s+", "", part, flags=re.I)
        for name in re.split(r"\s+(?:and|&)\s+", part):
            name = re.sub(r"(\s+(CDG|CSA))+$", "", name.strip(" .,"))
            if name:
                out.append((r, name))
    return out


kept, rejected, seen, unconfirmed = [], defaultdict(list), set(), []


def code(why):
    w = why.lower()
    return ("conflicting" if w.startswith("sources disagree") else "no_source" if w.startswith("no source") else
            "not_on_page" if w.startswith("name not on") else "show_missing" if "the show isn't" in w else
            "role_missing" if "next to the role" in w else "unavailable")
files = sorted(LOOKUPS.glob("*.json")) if LOOKUPS.exists() else []
for f in files:
    for rec in json.loads(f.read_text()):
        show = (rec.get("Production Name") or "").strip()
        src = rec.get("Sources") or {}
        # the venue counts only if one of its cited pages names both it and the show
        venue = "Venue not stated"
        v = (rec.get("Venue") or "").strip()
        if v.lower() not in SKIP and v.lower() != "conflicting":
            for url in src.get("Venue", []):
                text, _ = page_text(url)
                if text and contains(text, v.split(",")[0]) and contains(text, show):
                    venue = v
                    break
        # one node per production: the same show at another venue is a different production with its own team
        label = "%s (%s)" % (show, venue.split(",")[0]) if venue != "Venue not stated" else show
        for field in ("Casting Director", "Director", "Writer"):
            value = (rec.get(field) or "").strip()
            if value.lower() in SKIP:
                continue
            if value.lower() == "conflicting":
                rejected["Sources disagree (the skill said Conflicting)"].append("%s · %s · %s" % (show, field, ", ".join(src.get(field, []))))
                unconfirmed.append({"show": show, "role": field, "name": "", "reason": "conflicting", "urls": src.get(field, [])})
                continue
            if not src.get(field):
                rejected["No source given"].append("%s · %s: %s" % (show, field, value))
                unconfirmed.append({"show": show, "role": field, "name": value, "reason": "no_source", "urls": []})
                continue
            for role, name in people(field, value):
                why = "name not on any cited page"
                for url in src[field]:
                    text, err = page_text(url)
                    if err:
                        why = err
                        continue
                    if not contains(text, name):
                        continue
                    if not contains(text, show) and not contains(urlparse(url).path.replace("-", " "), show):
                        why = "name is on the page, but the show isn't"
                        continue
                    ev = role_evidence(text, name, role)
                    if not ev:
                        why = "name is on the page, but not next to the role (%s)" % role.lower()
                        continue
                    k = (key(name), role, key(label))
                    if k not in seen:
                        seen.add(k)
                        kept.append({"person": name, "role": role, "production": label, "venue": venue, "url": url,
                                     "evidence": around(ev, name), "rule": "K", "lookup_file": f.name})
                    why = None
                    break
                if why:
                    rejected[why[0].upper() + why[1:]].append("%s · %s: %s · %s" % (show, role, name, ", ".join(src[field])))
                    unconfirmed.append({"show": show, "role": role, "name": name, "reason": code(why), "urls": src[field]})

PAGES.write_text(json.dumps(pages, indent=1, ensure_ascii=False))
(OUT / "lookup_credits.json").write_text(json.dumps(kept, indent=1, ensure_ascii=False))
(OUT / "unconfirmed.json").write_text(json.dumps(unconfirmed, indent=1, ensure_ascii=False))
print("lookup files %d · kept %d · not used %d" % (len(files), len(kept), sum(len(v) for v in rejected.values())))
for why, rows in rejected.items():
    print("  %s: %d" % (why, len(rows)))
