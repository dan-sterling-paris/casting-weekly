"""Tests for rule G1 using real credit blocks seen on theatre pages (Leeds Playhouse, Royal Lyceum),
plus cases that must give nothing. Run: python3 test_g1.py"""
from rules import label_pairs

LEEDS = """Cast
Matthew Anthony Ralph
Romeo
Lauren Conroy
Juliet
Creatives
William Shakespeare
Writer
Chelsea Walker
Director
Georgia Lowe
Designer
Max Perryment
Composer
Pete Malkin
Sound Designer
Lizzie Powell
Lighting Designer
Becky Paris
Casting Director
Carter Ferguson
Fight Director"""

LYCEUM = """Cast and Credits
Directors
Katie Beard and Bobby Delaney
Musical Director
Bobby Delaney
Choreographer
Katie Beard
Puppetry Director
Sam Wilde"""

TRAP = """Associate Director
Jo Smith
Director
Ann Lee"""

MIXED = """Director
Ann Lee
Bob Jones
Writer"""

PROSE = "This new production will be directed by Thom Southerland and casting by Debbie O'Brien."


def got(text):
    found, status = label_pairs(text)
    return status, sorted((role, name) for _, role, name, _ in found)


def check(name, text, status, expected):
    st, pairs = got(text)
    ok = st == status and pairs == sorted(expected)
    print("%-6s %-7s status=%-5s %s" % ("PASS" if ok else "FAIL", name, st, pairs))
    return ok


results = [
    check("leeds", LEEDS, "ok", [("Writer", "William Shakespeare"), ("Director", "Chelsea Walker"), ("Composer", "Max Perryment"), ("Casting director", "Becky Paris")]),
    check("lyceum", LYCEUM, "ok", [("Director", "Katie Beard"), ("Director", "Bobby Delaney"), ("Choreographer", "Katie Beard")]),
    check("trap", TRAP, "ok", [("Director", "Ann Lee")]),
    check("mixed", MIXED, "mixed", []),
    check("prose", PROSE, "none", []),
]
print("all passed" if all(results) else "SOME FAILED")
