"""productions.txt is a queue: shows waiting to be looked up. No AI.

  python3 pipeline/todo.py                              list the shows waiting (and drop any already looked up)
  python3 pipeline/todo.py done <json> "<line>" ...     move those lines from the queue to lookups/done.txt

A show already in done.txt is never looked up again; if it is added to the queue a second time it is removed.
Case, punctuation and curly apostrophes are ignored when comparing. To redo a show, delete it from done.txt
and add it to the queue again.
"""
import sys
from common import ROOT, key

QUEUE = ROOT / "productions.txt"
DONE = ROOT / "lookups" / "done.txt"


def read(path):
    return path.read_text().splitlines() if path.exists() else []


def is_show(line):
    return line.strip() and not line.strip().startswith("#")


def done_keys():
    return {key(x.split("→")[0]) for x in read(DONE) if is_show(x)}


def write_queue(keep):
    header = [x for x in read(QUEUE) if not is_show(x)]
    QUEUE.write_text("\n".join(header + keep) + "\n")


if len(sys.argv) > 3 and sys.argv[1] == "done":
    batch, finished = sys.argv[2], sys.argv[3:]
    with DONE.open("a") as f:
        for line in finished:
            f.write("%s  →  %s\n" % (line.strip(), batch))
    gone = {key(x) for x in finished}
    write_queue([x.strip() for x in read(QUEUE) if is_show(x) and key(x) not in gone])
    print("moved %d to done.txt" % len(finished))
else:
    done, keep, dropped = done_keys(), [], []
    for x in (x.strip() for x in read(QUEUE) if is_show(x)):
        (dropped if key(x) in done else keep).append(x)
    if dropped:
        write_queue(keep)
        print("already looked up, removed from the queue: " + "; ".join(dropped))
    print("\n".join(keep) if keep else "Nothing new to look up")
