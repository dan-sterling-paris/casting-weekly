"""Build the Casting Weekly site from the confirmed credits.

  python3 pipeline/extract.py

Reads pipeline/out/lookup_credits.json (check_lookups.py), pipeline/out/names.json (match_names.py: other spellings
of the same person), the queue in pipeline/productions.txt and the "remove:" lines in pipeline/name_rules.txt
(granted takedowns). Writes site/index.html from site/template.html.
"""
import json
import re
from collections import defaultdict
from common import OUT, ROOT, key, now

SMALL = {"a", "an", "and", "at", "by", "for", "in", "of", "on", "or", "the", "to", "with"}
SITE = ROOT.parent / "site"


def load(name, default):
    f = OUT / name
    return json.loads(f.read_text()) if f.exists() else default


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


def batch_order(name):
    """2026-11-17-10.json sorts after 2026-11-17-9.json."""
    m = re.match(r"(.*)-(\d+)\.json$", name or "")
    return (m.group(1), int(m.group(2))) if m else (name or "", 0)


names = load("names.json", {})
ALIASES = names.get("aliases", {})
credits = load("lookup_credits.json", [])
batches = {f: i + 1 for i, f in enumerate(sorted({c.get("lookup_file") for c in credits}, key=batch_order))}

# granted takedowns: "remove: Name" drops a person, "remove: Name | Show" drops one credit
REMOVE_PERSON, REMOVE_CREDIT = set(), set()
rules = ROOT / "name_rules.txt"
for line in rules.read_text().splitlines() if rules.exists() else []:
    line = line.split("#", 1)[0].strip()
    if line.lower().startswith("remove:"):
        who, _, show = (x.strip() for x in line[7:].partition("|"))
        (REMOVE_CREDIT.add((key(who), key(show))) if show else REMOVE_PERSON.add(key(who)))

edges, shows, people, seen, removed = [], {}, {}, set(), 0
for c in credits:
    credited = c["person"].replace("’", "'")
    real = ALIASES.get(c["person"], c["person"])
    person = people.setdefault(key(real), real.replace("’", "'"))
    label, venue = c["production"], c["venue"]
    suffix = " (%s)" % venue.split(",")[0]
    show = label[: -len(suffix)] if venue != "Venue not stated" and label.endswith(suffix) else label
    if key(person) in REMOVE_PERSON or key(credited) in REMOVE_PERSON or \
            (key(person), key(show)) in REMOVE_CREDIT or (key(person), key(label)) in REMOVE_CREDIT:
        removed += 1
        continue
    k = (key(person), c["role"], key(label))
    if k in seen:
        continue
    seen.add(k)
    shows.setdefault(key(label), (title_case(label), title_case(show)))
    edges.append({"person": person, "role": c["role"], "production": shows[key(label)][0], "show": shows[key(label)][1],
                  "venue": venue, "url": c["url"], "evidence": c["evidence"], "batch": batches.get(c.get("lookup_file"), 0),
                  "credited_as": credited if key(credited) != key(person) else None})

done = {key(x.split("→")[0]) for x in (ROOT / "lookups" / "done.txt").read_text().splitlines()
        if x.strip() and not x.startswith("#")} if (ROOT / "lookups" / "done.txt").exists() else set()
queue = [x.strip() for x in (ROOT / "productions.txt").read_text().splitlines()
         if x.strip() and not x.strip().startswith("#") and key(x) not in done]

data = {"edges": edges, "queue": queue, "updated": now()[:10]}
blob = json.dumps(data, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
(SITE / "index.html").write_text((SITE / "template.html").read_text().replace("__DATA__", blob))

cd = defaultdict(int)
for e in edges:
    if e["role"] == "Casting director":
        cd[e["person"]] += 1
print("credits %d · shows %d · people %d · queued %d · removed by request %d · casting directors: %s" % (
    len(edges), len(shows), len(people), len(queue), removed, dict(sorted(cd.items(), key=lambda x: -x[1]))))
