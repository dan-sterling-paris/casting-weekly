"""Build the clickable catalogue prototype from checked entries.

Usage: python3 prototype/build.py [catalogue/runs/2026-11-16/entries.json]
Writes prototype/catalogue.html from prototype/catalogue.template.html.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "catalogue/runs/2026-11-16/entries.json"

# Where each theatre in the test sample is (public knowledge, used only for the region filter).
THEATRES = {
    "leeds-playhouse": ("Leeds", "Yorkshire"), "sheffield-theatres": ("Sheffield", "Yorkshire"),
    "royal-exchange": ("Manchester", "North West"), "bristol-old-vic": ("Bristol", "South West"),
    "nottingham-playhouse": ("Nottingham", "East Midlands"), "lyceum": ("Edinburgh", "Scotland"),
    "northern-stage": ("Newcastle", "North East"), "everyman-playhouse": ("Liverpool", "North West"),
    "new-vic": ("Newcastle-under-Lyme", "West Midlands"), "octagon": ("Bolton", "North West"),
    "sjt": ("Scarborough", "Yorkshire"), "hull-truck": ("Hull", "Yorkshire"),
}
LABELS = [("title", "Title"), ("venue", "Venue"), ("first_performance", "First date listed"),
          ("last_performance", "Last date listed"), ("producer", "Produced or presented by"),
          ("writer", "Writer"), ("director", "Director"), ("casting_director", "Casting director"),
          ("cast_announced", "Cast")]


def show(field, value):
    if field in ("first_performance", "last_performance"):
        return date.fromisoformat(value).strftime("%a %-d %b %Y")
    if field == "cast_announced":
        return "Cast announced on the theatre's page"
    return str(value)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70]


def main():
    data = json.loads(SRC.read_text())
    sources = {s["id"]: s for s in json.loads((HERE.parent / "catalogue/sources.json").read_text())["sources"]}
    prods = []
    for e in data["kept"]:
        f = e["facts"]
        g = lambda k: f[k]["value"] if k in f else None
        city, region = THEATRES[e["source_id"]]
        prods.append({
            "id": slug(e["source_id"] + "-" + f["title"]["value"]), "title": g("title"),
            "theatre": e["source_name"], "theatreId": e["source_id"], "city": city, "region": region,
            "venue": g("venue"), "first": g("first_performance"), "last": g("last_performance"),
            "producer": g("producer"), "writer": g("writer"), "director": g("director"),
            "castingDirector": g("casting_director"), "cast": bool(g("cast_announced")),
            "pageUrl": e["page_url"],
            "facts": [{"label": lab, "display": show(k, f[k]["value"]), "evidence": f[k]["evidence"]}
                      for k, lab in LABELS if k in f],
        })
    prods.sort(key=lambda p: (p["first"], p["title"]))
    theatres = [{"id": i, "name": s["name"], "url": s["url"], "city": THEATRES[i][0], "region": THEATRES[i][1]}
                for i, s in sources.items()]
    payload = {"checked": "16 Nov 2026", "productions": prods, "theatres": theatres}
    blob = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    tpl = (HERE / "catalogue.template.html").read_text()
    (HERE / "catalogue.html").write_text(tpl.replace("__DATA__", blob))
    people = set()
    for p in prods:
        for k in ("writer", "director", "castingDirector"):
            if p[k]:
                people.update(x.strip() for x in re.split(r"\s+and\s+", p[k]))
    print("embedded %d productions, %d theatres, %d people" % (len(prods), len(theatres), len(people)))


if __name__ == "__main__":
    main()
