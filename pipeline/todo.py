"""Which shows in productions.txt still need looking up? No AI.

  python3 pipeline/todo.py

Prints only the lines that aren't in pipeline/lookups/done.txt yet. Case, punctuation and curly apostrophes
are ignored when comparing, so "wicked, london" counts as already done if "Wicked, London" is.
To research a show again, delete its line from done.txt.
"""
import sys
from pathlib import Path
from common import ROOT, key

LIST = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "productions.txt"
DONE = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "lookups" / "done.txt"


def lines(path):
    if not path.exists():
        return []
    rows = [x.split("→")[0].strip() for x in path.read_text().splitlines()]
    return [x for x in rows if x and not x.startswith("#")]


done = {key(x) for x in lines(DONE)}
todo = [x for x in lines(LIST) if key(x) not in done]
print("\n".join(todo) if todo else "Nothing new to look up")
