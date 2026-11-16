"""Lightweight industry graph from saved pages, using pattern rules only (no AI).
Usage: python3 catalogue/graph_lite.py  -> writes prototype/industry-graph.html"""
import glob, json, re
from pathlib import Path
NAME = r"([A-Z][A-Za-z'’.\-]+(?:[ ](?:[A-Z][A-Za-z'’.\-]+|de|van|von|O’|O')){1,3})"
ROLES = {"director":"Director","directed by":"Director","casting director":"Casting director","casting by":"Casting director",
         "cast by":"Casting director","casting":"Casting director","writer":"Writer","written by":"Writer","playwright":"Writer",
         "choreographer":"Choreographer","choreography by":"Choreographer","designer":"Designer","composer":"Composer"}
BAD = re.compile(r"Theatre|Playhouse|Company|Productions?|Lyceum|Stage|Exchange|Studio|Festival|Young|Associate|Assistant|Artistic|Book|Tickets?|Cast|The\b|Our\b", re.I)
QUAL = re.compile(r"(Associate|Assistant|Fight|Intimacy|Movement|Musical|Music|Artistic|Video|Lighting|Sound|Resident|Co-|Deputy|Executive|Casting|Creative|Production|Technical|Puppetry|Voice|Dialect|Film)[ &,]*(&[ ]*\w+[ ]*)?$", re.I)
inline = re.compile(r"\b(Directed by|Casting by|Cast by|Written by|Choreography by|Casting Director|Director|Writer|Choreographer)[,:]?[ ]+" + NAME)
twoline = re.compile(r"^" + NAME + r"(?:\s+CDG|\s+CSA)?\n(Director|Casting Director|Writer|Choreographer|Designer|Composer|Playwright)$", re.M)
edges, seen = [], set()
for f in glob.glob("catalogue/cache/2026-11-16/*.txt") + glob.glob("catalogue/cache/people/*.txt"):
    t = Path(f).read_text(); lines = t.split("\n")
    url = lines[0][5:]; title = re.split(r"\s[|\-–]\s", lines[1][7:])[0].strip()
    venue = Path(f).name.rsplit("-", 1)[0]
    if "unitedagents" in f: continue  # an agent's CV page: its layout needs its own rule, left out of this test
    if re.search(r"\((U|PG|12A|15|18)\)|\(\d{4}", lines[1]): continue
    found = [(m.group(1), m.group(2), m.group(0)) for m in inline.finditer(t)
             if not (m.group(1).lower() in ("director", "casting director") and QUAL.search(t[max(0, m.start()-30):m.start()].split("\n")[-1]))
             and not (m.group(1) == "Director" and t[max(0, m.start()-8):m.start()].endswith("Casting "))] + [(m.group(2), m.group(1), m.group(0).replace("\n", " ")) for m in twoline.finditer(t) if not QUAL.search(t[max(0, m.start()-30):m.start()].split("\n")[-1] if False else "")]
    for role, name, ev in found:
        name = re.sub(r"(\s+(CDG|CSA))+$", "", name.strip().rstrip(".")).replace("’", "'")
        if BAD.search(name) or len(name) > 40: continue
        key = (name.lower(), title.lower(), ROLES[role.lower()])
        if key in seen: continue
        seen.add(key); edges.append({"person": name, "role": ROLES[role.lower()], "production": title, "venue": venue, "url": url, "evidence": ev})
data = json.dumps({"edges": edges}, ensure_ascii=False).replace("</", "<\\/")
tpl = Path("prototype/industry-graph.template.html").read_text()
Path("prototype/industry-graph.html").write_text(tpl.replace("__DATA__", data))
print(len(edges), "credits;", len({e["person"] for e in edges}), "people;", len({e["production"] for e in edges}), "productions")
