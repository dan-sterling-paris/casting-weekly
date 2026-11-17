"""Find people credited under more than one spelling (e.g. "Natalia Gallacher" / "Natalie Gallacher") with Splink.

  python3 pipeline/match_names.py        (after check_lookups.py, before extract.py)

Splink scores every pair of names that could be the same person, using:
  - first name and surname (exact, or close spelling by Jaro-Winkler)
  - the people they were credited alongside (a typo'd name still shares co-workers with the right one)
  - whether both are casting credits or both are creative credits
A "Pippa Ailion Casting" style company name is compared as the person it is named after.

The model's match weights (m) are set by hand below, so the result does not swing on a small data set;
how common each agreement is by chance (u) is measured from the names themselves, with a fixed seed.

Two names that the same page credits separately (e.g. "Abner Ramirez" and "Amanda Ramirez") are never merged.
Pairs scoring at least AUTO are merged on the graph under the spelling with the most credits.
Pairs between REVIEW and AUTO are only listed. pipeline/name_rules.txt overrides both.

Reads pipeline/out/lookup_credits.json and pipeline/name_rules.txt.
Writes pipeline/out/name_aliases.json (used by extract.py) and pipeline/out/NAME_MATCHES.md.
"""
import json
import logging
import re
import unicodedata
from collections import defaultdict

import pandas as pd
import splink.comparison_level_library as cll
from splink import DuckDBAPI, Linker, SettingsCreator, block_on
from splink.comparison_library import CustomComparison

from common import OUT, ROOT

AUTO, REVIEW = 0.95, 0.80
RULES = ROOT / "name_rules.txt"
logging.disable(logging.WARNING)


def norm(name):
    """Lower case, no accents or punctuation; "Pippa Ailion Casting" -> "pippa ailion" (a one-word firm like "Pearson Casting" stays)."""
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().casefold()
    s = re.sub(r"[^a-z0-9 ]+", " ", s.replace("'", "")).split()
    s = [w for w in s if w not in ("cdg", "csa")]
    if len(s) >= 3 and s[-1] == "casting":
        s = s[:-1]
    return " ".join(s)


def read_rules():
    same, apart = {}, set()
    for line in RULES.read_text().splitlines() if RULES.exists() else []:
        line = line.split("#", 1)[0].strip()
        if line.lower().startswith("same:") and "=" in line:
            a, b = (x.strip() for x in line[5:].split("=", 1))
            same[a] = b
        elif line.lower().startswith("different:") and "|" in line:
            a, b = (x.strip() for x in line[10:].split("|", 1))
            apart.add(frozenset((a, b)))
    return same, apart


credits = json.loads((OUT / "lookup_credits.json").read_text())
prods_of, group_of, urls_of = defaultdict(set), {}, defaultdict(set)
for c in credits:
    prods_of[c["person"]].add(c["production"])
    urls_of[c["person"]].add(c["url"])
    if c["role"] == "Casting director" or group_of.get(c["person"]) != "casting":
        group_of[c["person"]] = "casting" if c["role"] == "Casting director" else "creative"
people_on = defaultdict(set)
for p, prods in prods_of.items():
    for pr in prods:
        people_on[pr].add(p)

names = sorted(prods_of)
rows = []
for i, name in enumerate(names):
    parts = norm(name).split() or [""]
    coworkers = sorted({norm(q) for pr in prods_of[name] for q in people_on[pr] if q != name})
    rows.append({"unique_id": i, "name": name, "first_name": parts[0], "surname": parts[-1] if len(parts) > 1 else None,
                 "coworkers": coworkers, "grp": group_of[name]})
df = pd.DataFrame(rows)


def name_levels(col, exact_m, close_m):
    return CustomComparison(output_column_name=col, comparison_levels=[
        cll.NullLevel(col),
        cll.ExactMatchLevel(col).configure(m_probability=exact_m),
        cll.JaroWinklerLevel(col, 0.92).configure(m_probability=close_m),
        cll.JaroWinklerLevel(col, 0.80).configure(m_probability=0.03),
        cll.ElseLevel().configure(m_probability=1 - exact_m - close_m - 0.03),
    ])


settings = SettingsCreator(
    link_type="dedupe_only",
    probability_two_random_records_match=0.01,
    blocking_rules_to_generate_predictions=[block_on("surname"), block_on("first_name"),
                                            block_on("substr(surname, 1, 3)"), block_on("substr(first_name, 1, 3)")],
    comparisons=[
        name_levels("first_name", 0.82, 0.12),
        name_levels("surname", 0.90, 0.06),
        CustomComparison(output_column_name="coworkers", comparison_levels=[
            cll.NullLevel("coworkers"),
            cll.ArrayIntersectLevel("coworkers", 2).configure(m_probability=0.50),
            cll.ArrayIntersectLevel("coworkers", 1).configure(m_probability=0.30),
            cll.ElseLevel().configure(m_probability=0.20),
        ]),
        CustomComparison(output_column_name="grp", comparison_levels=[
            cll.NullLevel("grp"),
            cll.ExactMatchLevel("grp").configure(m_probability=0.85),
            cll.ElseLevel().configure(m_probability=0.15),
        ]),
    ],
    retain_intermediate_calculation_columns=False,
)

pairs = []
if len(df) > 1:
    linker = Linker(df, settings, db_api=DuckDBAPI())
    linker.training.estimate_u_using_random_sampling(max_pairs=1e7, seed=1)
    pred = linker.inference.predict(threshold_match_probability=REVIEW).as_pandas_dataframe()
    for r in pred.itertuples():
        pairs.append((names[int(r.unique_id_l)], names[int(r.unique_id_r)], float(r.match_probability)))
pairs.sort(key=lambda x: -x[2])

same, apart = read_rules()
parent = {n: n for n in names}


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


merged, review = [], []
for a, b, p in pairs:
    if frozenset((a, b)) in apart or urls_of[a] & urls_of[b]:   # one page naming both means two people
        continue
    if p >= AUTO:
        parent[find(a)] = find(b)
        merged.append((a, b, p))
    else:
        review.append((a, b, p))
for a, b in same.items():
    if a in parent and b in parent:
        parent[find(a)] = find(b)

clusters = defaultdict(list)
for n in names:
    clusters[find(n)].append(n)
forced = set(same.values())
aliases = {}
for members in clusters.values():
    if len(members) < 2:
        continue
    # the spelling shown: one named on the right of a "same:" rule, else the one with most productions, then most pages
    canon = max(members, key=lambda n: (n in forced, len(prods_of[n]), len(urls_of[n]), -len(n), n))
    for n in members:
        if n != canon:
            aliases[n] = canon

(OUT / "name_aliases.json").write_text(json.dumps(aliases, indent=1, ensure_ascii=False, sort_keys=True))
md = ["# Names that may be the same person", "",
      "Scored by Splink (`pipeline/match_names.py`). Merged pairs are shown on the graph under one spelling; "
      "each credit still quotes the spelling its source used. To change a decision, add a line to "
      "`pipeline/name_rules.txt`.", "", "## Merged (match probability %.0f%% or more)" % (AUTO * 100), ""]
md += ["- %s / %s → shown as **%s** · %.1f%%" % (a, b, aliases.get(a, a) if a in aliases else aliases.get(b, b), p * 100)
       for a, b, p in merged] or ["- none"]
md += ["", "## Merged by name_rules.txt", ""] + (["- %s → **%s**" % (a, b) for a, b in same.items()] or ["- none"])
md += ["", "## For review (%.0f–%.0f%%), not merged" % (REVIEW * 100, AUTO * 100), ""]
md += ["- %s / %s · %.1f%% · to merge: `same: %s = %s` · to dismiss: `different: %s | %s`" % (a, b, p * 100, a, b, a, b)
       for a, b, p in review] or ["- none"]
(OUT / "NAME_MATCHES.md").write_text("\n".join(md) + "\n")
print("names %d · merged %d · for review %d · %s" % (len(names), len(aliases), len(review),
      "; ".join("%s → %s" % kv for kv in sorted(aliases.items())) or "no merges"))
