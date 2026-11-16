"""Deterministic checker for Casting Weekly catalogue entries. Python standard library only.

Claude proposes entries ("readings"); this script decides what survives. A fact is kept only if
  * its evidence appears word for word in the saved page text,
  * every meaningful word of the value appears in that evidence (dates are compared as dates), and
  * the second, independent reading gives the same value.
An entry is dropped if a required fact fails or its first performance is outside the window.

Usage:
  python3 catalogue/verify.py reading1.json reading2.json --out entries.json \
      [--from 2026-11-17] [--to 2027-11-16]
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

REQUIRED = ["title", "venue", "first_performance"]
OPTIONAL = ["producer", "last_performance", "writer", "director", "casting_director", "cast_announced"]
DATE_FIELDS = {"first_performance", "last_performance"}
STOP = set("the a an and or of to in on for with at by from is are be as this that our your their its it we you will".split())
MONTHS = {m: i + 1 for i, m in enumerate("january february march april may june july august september october november december".split())}
MONTHS.update({m[:3]: i for m, i in list(MONTHS.items())})
MONTHS["sept"] = 9
WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def norm(s):
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), (" ", " "), (" ", " ")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def words(s):
    return [w for w in re.findall(r"[a-z0-9£']+", norm(str(s)).lower()) if w not in STOP and len(w) > 1]


def _mk(y, m, d):
    try:
        return date(int(y), int(m), int(d))
    except ValueError:
        return None


def dates_in(text, default_year):
    t = norm(text).lower()
    out = []
    # ranges like "3 - 20 Dec 2026" give both days
    for d1, d2, m, y in re.findall(r"\b(\d{1,2})(?:st|nd|rd|th)?\s*-\s*(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]{3,9})\.?,?\s*(\d{4})?", t):
        if m in MONTHS:
            out += [_mk(y or default_year, MONTHS[m], d1), _mk(y or default_year, MONTHS[m], d2)]
    # "Tue 4 Sat 8 May 2027": a first day with no month, then the closing date (both weekdays must match)
    for wd1, d1, wd2, d2, m, y in re.findall(r"\b(mon|tue|wed|thu|fri|sat|sun)[a-z]*\.?\s+(\d{1,2})\s+(?:-\s*)?(mon|tue|wed|thu|fri|sat|sun)[a-z]*\.?\s+(\d{1,2})\s+([a-z]{3,9})\.?\s*(\d{4})?", t):
        if m in MONTHS:
            a, b = _mk(y or default_year, MONTHS[m], d1), _mk(y or default_year, MONTHS[m], d2)
            if a and b and a.weekday() == WEEKDAYS.index(wd1) and b.weekday() == WEEKDAYS.index(wd2):
                out += [a, b]
    for wd, d, m, y in re.findall(r"\b(?:(mon|tue|wed|thu|fri|sat|sun)[a-z]*\.?,?\s+)?(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?([a-z]{3,9})\.?,?\s*(\d{4})?", t):
        if m in MONTHS:
            x = _mk(y or default_year, MONTHS[m], d)
            # a weekday printed on the page must match the date, which pins the year
            if x and wd and WEEKDAYS.index(wd) != x.weekday():
                continue
            out.append(x)
    for m, d, y in re.findall(r"\b([a-z]{3,9})\.?\s+(\d{1,2})(?!\d)(?:st|nd|rd|th)?,?\s*(\d{4})?", t):
        if m in MONTHS:
            out.append(_mk(y or default_year, MONTHS[m], d))
    for d, m, y in re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", t):
        out.append(_mk(int(y) + 2000 if len(y) == 2 else y, m, d))
    return [x for x in out if x]


def check_fact(name, fact, page):
    if not fact or fact.get("value") in (None, "", False) or not fact.get("evidence"):
        return False, "missing"
    ev = norm(fact["evidence"])
    if ev.lower() not in page.lower():
        return False, "evidence not on the page word for word"
    val = fact["value"]
    if name in DATE_FIELDS:
        try:
            d = date.fromisoformat(str(val))
        except ValueError:
            return False, "not an ISO date"
        found = sorted(set(dates_in(ev, d.year)))
        if d not in found:
            return False, "date not in the evidence"
        if not re.search(r"\b20\d\d\b", ev) and not re.search(r"\b(mon|tue|wed|thu|fri|sat|sun)", ev, re.I):
            return False, "the evidence shows no year or weekday, so the year can't be confirmed"
        if name == "first_performance" and d != found[0]:
            return False, "not the earliest date in the evidence"
        if name == "last_performance" and d != found[-1]:
            return False, "not the latest date in the evidence"
        return True, ""
    if name == "cast_announced":
        return (True, "") if re.search(r"\bcast\b|starring|\bwith\b", ev, re.I) else (False, "evidence doesn't mention cast")
    ev_words = set(words(ev))
    missing = [w for w in words(val) if w not in ev_words]
    return (False, "value words not in evidence: " + ", ".join(missing[:4])) if missing else (True, "")


def same(a, b):
    if not a or not b:
        return not a and not b
    if isinstance(a.get("value"), bool) or isinstance(b.get("value"), bool):
        return a.get("value") == b.get("value")
    return words(a.get("value", "")) == words(b.get("value", ""))


def key(e):
    return (e["source_id"], " ".join(words(e["fields"].get("title", {}).get("value", ""))))


def main():
    a = sys.argv[1:]
    out = Path(a[a.index("--out") + 1])
    lo = date.fromisoformat(a[a.index("--from") + 1]) if "--from" in a else date(2026, 11, 17)
    hi = date.fromisoformat(a[a.index("--to") + 1]) if "--to" in a else date(2027, 11, 16)
    r1 = json.loads(Path(a[0]).read_text())["entries"]
    r2 = {key(e): e for e in json.loads(Path(a[1]).read_text())["entries"]}
    kept, dropped, seen = [], [], set()
    for e in r1:
        page = norm(Path(e["cache"]).read_text()) if Path(e["cache"]).exists() else ""
        other = r2.get(key(e))
        res = {"source_id": e["source_id"], "source_name": e["source_name"], "page_url": e["page_url"],
               "facts": {}, "left_out": [], "problems": []}
        if not page:
            res["problems"].append("page text not available")
        if other is None:
            res["problems"].append("the second reading did not find this production")
        for name in REQUIRED + OPTIONAL:
            ok, why = check_fact(name, e["fields"].get(name), page)
            if ok and other is not None and not same(e["fields"].get(name), other["fields"].get(name)):
                ok, why = False, "the two readings disagree"
            if ok:
                res["facts"][name] = e["fields"][name]
            elif name in REQUIRED:
                res["problems"].append("%s: %s" % (name, why))
            elif e["fields"].get(name):
                res["left_out"].append("%s: %s" % (name, why))
        fp = res["facts"].get("first_performance")
        if fp and not lo <= date.fromisoformat(fp["value"]) <= hi:
            res["problems"].append("first performance %s is outside %s to %s" % (fp["value"], lo, hi))
        k = key(e)
        if not res["problems"] and k in seen:
            res["problems"].append("duplicate")
        (dropped if res["problems"] else kept).append(res)
        seen.add(k)
    out.write_text(json.dumps({"window": [lo.isoformat(), hi.isoformat()], "kept": kept, "dropped": dropped}, indent=1, ensure_ascii=False))
    print("kept %d, dropped %d" % (len(kept), len(dropped)))
    for d in dropped:
        print("  dropped %-20s %-40s %s" % (d["source_id"], (e.get("fields", {}).get("title", {}) or {}).get("value", "")[:0] + d["page_url"][-40:], "; ".join(d["problems"])[:120]))


if __name__ == "__main__":
    main()
