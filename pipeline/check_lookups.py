"""Check the production-credits-lookup skill's answers with no AI, before they reach the graph.

The skill (Claude) finds credits and the pages that state them; it saves its JSON, untouched, in pipeline/lookups/.
This script opens every cited page itself (robots.txt obeyed, 2 s per site) and keeps a credit only if that page's
text contains both the person's name and the production's name. Everything else is listed with the reason.

  python3 pipeline/check_lookups.py        then        python3 pipeline/extract.py

Writes pipeline/out/lookup_credits.json (kept) and pipeline/out/LOOKUP_REJECTED.md (not kept).
"""
import json
import re
from collections import defaultdict
from urllib.parse import urlparse
from common import CACHE, OUT, ROOT, UA, get, html_to_text, key, now, robots, sha
from rules import sentences

LOOKUPS = ROOT / "lookups"
PAGES = OUT / "lookup_pages.json"
SKIP = {"", "unknown"}
WRITER_PART = {"book": "Writer", "music": "Composer", "lyrics": "Lyricist", "music and lyrics": "Composer",
               "music & lyrics": "Composer", "adapted by": "Writer", "written by": "Writer", "playwright": "Writer"}

# the role must be stated next to the name: in the same sentence, or on the line just before or after it
ROLE_WORD = {"Casting director": r"casting", "Director": r"direct", "Writer": r"writ|book|creat|playwright|adapt|monologue|script",
             "Composer": r"music|compos|score", "Lyricist": r"lyric"}


def role_evidence(text, name, role):
    rx = re.compile(r"\b(?:%s)" % ROLE_WORD[role], re.I)
    for s in sentences(text):
        if contains(s, name) and rx.search(s):
            return s
    lines = [x.strip() for x in text.split("\n")]
    for i, line in enumerate(lines):
        if contains(line, name) and len(line) < 80:   # a short label/name line, e.g. "Director -" then "Joe Mantello"
            near = [lines[j] for j in (i - 1, i + 1) if 0 <= j < len(lines)]
            if any(rx.search(x) and len(x) < 60 for x in near):
                return " / ".join([lines[i - 1], line] if i and rx.search(lines[i - 1]) else [line, lines[i + 1]])
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


kept, rejected, seen = [], defaultdict(list), set()
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
        for field in ("Casting Director", "Director", "Writer"):
            value = (rec.get(field) or "").strip()
            if value.lower() in SKIP:
                continue
            if value.lower() == "conflicting":
                rejected["Sources disagree (the skill said Conflicting)"].append("%s · %s · %s" % (show, field, ", ".join(src.get(field, []))))
                continue
            if not src.get(field):
                rejected["No source given"].append("%s · %s: %s" % (show, field, value))
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
                    k = (key(name), role, key(show))
                    if k not in seen:
                        seen.add(k)
                        kept.append({"person": name, "role": role, "production": show, "venue": venue, "url": url,
                                     "evidence": ev[:400], "rule": "K", "lookup_file": f.name})
                    why = None
                    break
                if why:
                    rejected[why[0].upper() + why[1:]].append("%s · %s: %s · %s" % (show, role, name, ", ".join(src[field])))

PAGES.write_text(json.dumps(pages, indent=1, ensure_ascii=False))
(OUT / "lookup_credits.json").write_text(json.dumps(kept, indent=1, ensure_ascii=False))
md = ["# Lookup answers not used", "", "Found by the production-credits-lookup skill, but the check script could not confirm them "
      "on the cited page, so they are not in the network.", ""]
for why, rows in rejected.items():
    md += ["## %s (%d)" % (why, len(rows)), ""] + ["- " + r for r in rows] + [""]
(OUT / "LOOKUP_REJECTED.md").write_text("\n".join(md))
print("lookup files %d · kept %d · not used %d" % (len(files), len(kept), sum(len(v) for v in rejected.values())))
for why, rows in rejected.items():
    print("  %s: %d" % (why, len(rows)))
