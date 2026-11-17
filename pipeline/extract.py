"""Build the network page from the checked lookup credits. No fetching, no AI.

  python3 pipeline/extract.py

Reads pipeline/out/lookup_credits.json (written by check_lookups.py) and pipeline/out/name_aliases.json (written by
match_names.py: other spellings of the same person) and writes prototype/industry-intel.html.
"""
import json
import re
from collections import defaultdict
from common import OUT, ROOT, key, now

SMALL = {"a", "an", "and", "at", "by", "for", "in", "of", "on", "or", "the", "to", "with"}


def title_case(t):
    """Display a title written IN CAPITALS in normal capitals; keep short words in brackets as written (e.g. RSC)."""
    if t != t.upper():
        return t
    out = []
    for i, w in enumerate(t.split()):
        core = w.strip("()[]:,.!?'’\"")
        if w.startswith("(") and len(core) <= 4:
            out.append(w)
        elif i > 0 and core.lower() in SMALL:
            out.append(w.lower())
        else:
            out.append(re.sub(r"[A-Za-z][A-Za-z'’]*", lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(), w))
    return " ".join(out)


edges, shows, people, seen = [], {}, {}, set()


aliases_file = OUT / "name_aliases.json"
ALIASES = json.loads(aliases_file.read_text()) if aliases_file.exists() else {}


def add(person, role, show, org, rule, evidence, url, year=None):
    credited = person.replace("’", "'")
    person = people.setdefault(key(ALIASES.get(person, person)), ALIASES.get(person, person).replace("’", "'"))
    k = (key(person), role, key(show), year)
    if k in seen:
        return
    seen.add(k)
    shows.setdefault(key(show), title_case(show))
    edges.append({"person": person, "role": role, "production": shows[key(show)], "venue": org, "url": url,
                  "evidence": evidence, "rule": rule, "year": year,
                  "credited_as": credited if key(credited) != key(person) else None})


lookup_file = OUT / "lookup_credits.json"
for c in json.loads(lookup_file.read_text()) if lookup_file.exists() else []:
    add(c["person"], c["role"], c["production"], c["venue"], "K", c["evidence"], c["url"])

orgs = {e["venue"]: e["venue"] for e in edges}
data = json.dumps({"edges": edges, "theatres": orgs, "swept": now()[:10]}, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
tpl = (ROOT.parent / "prototype/industry-intel.template.html").read_text()
(ROOT.parent / "prototype/industry-intel.html").write_text(tpl.replace("__DATA__", data))

cd = defaultdict(int)
for e in edges:
    if e["role"] == "Casting director":
        cd[e["person"]] += 1
print("credits %d · shows %d · people %d · casting directors: %s" % (
    len(edges), len(shows), len(people), dict(sorted(cd.items(), key=lambda x: -x[1]))))
