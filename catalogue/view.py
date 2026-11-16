"""Print a saved page without the menu and footer lines its site repeats on every page.

Usage: python3 catalogue/view.py catalogue/cache/<date>/<site>-<hash>.txt
Only for reading; evidence must still be copied from the full page text, which this
prints unchanged apart from the dropped repeated lines.
"""
import sys
from collections import Counter
from pathlib import Path

f = Path(sys.argv[1])
site = f.name.rsplit("-", 1)[0]
pages = [p.read_text().splitlines() for p in f.parent.glob(site + "-*.txt")]
common = Counter(line for p in pages for line in set(p))
limit = max(2, len(pages) // 2)
seen = set()
for line in f.read_text().splitlines():
    if (common[line] >= limit and len(pages) > 2 and not line.startswith(("URL:", "TITLE:"))) or line in seen:
        continue
    seen.add(line)
    print(line)
