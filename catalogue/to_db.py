"""Turn checked entries (verify.py output) into documents for the checking page.

Usage: python3 catalogue/to_db.py entries.json OUT_DIR
Writes OUT_DIR/<doc id>.json (one per entry) and OUT_DIR/writes.json (a batch of set writes).
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

LABELS = [("title", "Title"), ("venue", "Venue"), ("first_performance", "First date listed"),
          ("last_performance", "Last date listed"), ("producer", "Produced or presented by"),
          ("writer", "Writer"), ("director", "Director"), ("casting_director", "Casting director"),
          ("cast_announced", "Cast")]


def show(field, value):
    if field in ("first_performance", "last_performance"):
        return date.fromisoformat(value).strftime("%a %-d %b %Y")
    if field == "cast_announced":
        return "Cast announced"
    return str(value)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80]


def main():
    data = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    kept = sorted(data["kept"], key=lambda e: (e["facts"]["first_performance"]["value"], e["source_name"]))
    writes = []
    for i, e in enumerate(kept, 1):
        f = e["facts"]
        doc_id = slug(e["source_id"] + "-" + f["title"]["value"])
        doc = {
            "order": i, "theatre": e["source_name"], "title": f["title"]["value"], "page_url": e["page_url"],
            "checked": "16 Nov 2026", "first_performance": f["first_performance"]["value"],
            "facts": [{"field": k, "label": label, "value": f[k]["value"], "display": show(k, f[k]["value"]),
                       "evidence": f[k]["evidence"]} for k, label in LABELS if k in f],
        }
        p = out / (doc_id + ".json")
        p.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
        writes.append({"op": "set", "collection": "entries", "doc_id": doc_id, "file_path": str(p)})
    (out / "writes.json").write_text(json.dumps(writes, indent=1))
    print(len(writes), "documents written to", out)


if __name__ == "__main__":
    main()
