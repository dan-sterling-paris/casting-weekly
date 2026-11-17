"""Pattern extraction: three general patterns, none written for a particular site. No AI.

  S  sentence   "casting by NAME", "Casting Director: NAME", "directed by NAME" ... inside a sentence
  L  label      a line that is exactly a role, next to a line that is only a name (either order)
  B  block      a show title IN CAPITALS followed, within a few lines and in any order, by
                "Casting Director", a year, a venue/company and "Dir. NAME" (agency CV style)

Anything a page has that matches none of these is left unread and listed, never guessed.
"""
import re

NAME = r"[A-Z][A-Za-z'’\-]+(?: (?:de|van|von|di|[A-Z][A-Za-z'’\-]+)){1,3}"
NAMES = r"(?P<names>" + NAME + r"(?:(?: and| &) " + NAME + r")*)(?: (?:CDG|CSA))*"
QUALIFIERS = r"(Associate|Assistant|Resident|Fight|Intimacy|Movement|Musical|Music|Artistic|Video|Lighting|Sound|Co-|Deputy|Executive|Creative|Production|Technical|Puppetry|Voice|Dialect|Children's|Children’s|Revival)"
QUAL_BEFORE = re.compile(QUALIFIERS + r"\s*(?:&\s*\w+\s*)?$", re.I)
NOT_A_NAME = re.compile(r"'s\b|’s\b|\b(Director|Artistic|Associate|Producer|Chief|Executive|Theatre|Productions?|Live|Company|Ltd|Limited|"
                        r"Group|Entertainment|Award|Awards|Tour|Musical|Season|West End|Broadway|London|UK)\b")
VENUE_WORDS = re.compile(r"\b(Playhouse|Palace|Theatre|Theater|Hall|House|Centre|Center|Coliseum|Studios?|Arena|Pavilion|Opera|Arts|Rep|Lyceum|Festival|Tour|Productions?)\b")


def split_names(s):
    return [re.sub(r"(\s+(CDG|CSA))+$", "", n.strip()) for n in re.split(r",| and | & ", s) if n.strip()]


def sentences(text):
    out = []
    for line in text.split("\n"):
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", line):
            if len(s.strip()) > 3:
                out.append(s.strip())
    return out


# ---------------- S: sentence pattern ----------------
SENTENCE = [
    ("Casting director", re.compile(r"\b[Cc]asting by " + NAMES)),
    ("Casting director", re.compile(r"\bCasting Director(?:s)?[,:]? " + NAMES)),
    ("Director", re.compile(r"\b[Dd]irected by " + NAMES)),
    ("Director", re.compile(r"(?<!\w)Director[,:] " + NAMES)),
    ("Choreographer", re.compile(r"\b(?:[Cc]horeography by|[Cc]horeographed by) " + NAMES)),
    ("Writer", re.compile(r"\b(?:[Ww]ritten by|[Bb]ook by) " + NAMES)),
]


def pattern_s(text):
    found = []
    for sent in sentences(text):
        for role, rx in SENTENCE:
            for m in rx.finditer(sent):
                if QUAL_BEFORE.search(sent[:m.start()]):
                    continue
                for n in split_names(m.group("names")):
                    if not NOT_A_NAME.search(n):
                        found.append(("S", role, n, sent))
    return found


# ---------------- L: label next to a name ----------------
ROLES = {
    "casting director": "Casting director", "casting directors": "Casting director", "casting": "Casting director", "casting by": "Casting director",
    "director": "Director", "directors": "Director", "directed by": "Director",
    "writer": "Writer", "writers": "Writer", "written by": "Writer", "playwright": "Writer", "book": "Writer", "book by": "Writer",
    "choreographer": "Choreographer", "choreography": "Choreographer", "choreography by": "Choreographer",
    "composer": "Composer", "music by": "Composer",
}
OTHER_JOB = re.compile(r"^(?:[A-Z][\w'’&/-]*\s?){0,4}(Director|Designer|Supervisor|Manager|Producer|Assistant|Associate|Arranger|"
                       r"Orchestrator|Orchestrations|Captain|Coach|Consultant|Lyricist|Lyrics|Dramaturg|Choreographer|Writer|Composer|"
                       r"Casting|Illusions|Puppetry|Swing|Understudy|Administrator|Administration)s?\b.*$")
NAME_LINE = re.compile(r"^(?P<names>" + NAME + r"(?:(?:,| and| &) " + NAME + r")*)(?: (?:CDG|CSA))*$")


def _kind(line):
    key = line.strip().rstrip(":").strip().lower()
    if key in ROLES:
        return ("role", ROLES[key])
    if OTHER_JOB.match(line.strip()):
        return ("other", None)
    m = NAME_LINE.match(line.strip())
    if m and not NOT_A_NAME.search(m.group("names")) and not VENUE_WORDS.search(m.group("names")):
        return ("name", m.group("names"))
    return (None, None)


def label_pairs(text):
    """Return (credits, status): status is 'ok', 'none', or 'mixed' (page uses both orders, so nothing is taken)."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    kinds = [_kind(l) for l in lines]
    runs, cur = [], []
    for i, (k, v) in enumerate(kinds):
        if k is None or (cur and (kinds[cur[-1]][0] == "name") == (k == "name")):
            if len(cur) >= 2:
                runs.append(cur)
            cur = [i] if k else []
            continue
        cur.append(i)
    if len(cur) >= 2:
        runs.append(cur)
    if not runs:
        return [], "none"
    orient = {"role-first" if kinds[r[0]][0] != "name" else "name-first" for r in runs}
    if len(orient) > 1:
        return [], "mixed"
    role_first = orient.pop() == "role-first"
    out = []
    for r in runs:
        for a, b in zip(r[0::2], r[1::2]):
            lab, nm = (a, b) if role_first else (b, a)
            if kinds[lab][0] == "role" and kinds[nm][0] == "name":
                for n in split_names(kinds[nm][1]):
                    out.append(("L", kinds[lab][1], n, lines[a] + " / " + lines[b]))
    return out, "ok"


def pattern_l(text):
    return label_pairs(text)


# ---------------- B: credit block ----------------
YEAR = re.compile(r"^(19|20)\d\d(\s*[–-]\s*(19|20)\d\d)?$")
CASTING_ROLE = re.compile(r"^(?:Co-)?Casting Director$", re.I)


def _is_title(line):
    return len(line) > 2 and line.upper() == line and re.search(r"[A-Z]{2}", line) and not YEAR.match(line)


def pattern_b(text, owner):
    """A CAPITALS title, then (in any order, within 5 lines, before the next title) 'Casting Director',
    optionally a year, a venue/company and 'Dir. Name'. The casting credit belongs to the page's owner."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    out = []
    for i, line in enumerate(lines):
        if not _is_title(line):
            continue
        block = []
        for nxt in lines[i + 1:i + 6]:
            if _is_title(nxt):
                break
            block.append(nxt)
        r = next((k for k, b in enumerate(block) if CASTING_ROLE.match(b)), None)
        if r is None:
            continue
        # between the title and the role only a year, a venue after the year, or a "Dir." line may sit
        between = block[:r]
        if any(not (YEAR.match(b) or b.startswith("Dir. ") or (k > 0 and YEAR.match(between[0]))) for k, b in enumerate(between)):
            continue
        year = next((b for b in block if YEAR.match(b)), None)
        dirs = [n for b in block if b.startswith("Dir. ") for n in split_names(b[5:])]
        # the venue/company is only ever the line before the role (after the year); otherwise it's not stated
        venue = next((b for b in reversed(between) if not YEAR.match(b) and not b.startswith("Dir. ")), None)
        role_line = next(b for b in block if CASTING_ROLE.match(b))
        evidence = " / ".join([line] + block[:4])
        out.append({"title": line, "year": year, "venue": venue, "role": role_line, "directors": dirs,
                    "owner": owner, "evidence": evidence})
    return out if len(out) >= 3 else []   # a CV lists several credits; a single heading is not a CV


# ---------------- which show a page is about (for S and L credits) ----------------
OF_TITLE = re.compile(r"(?:production|season) of (?:the )?(?:musical |hit musical |classic )?(?P<t>(?:[A-Z][\w'’&!:\-]*)(?: (?:of|the|and|in|a|to|on|\+|&|[A-Z][\w'’&!:\-]*))*)")
CAPS_TITLE = re.compile(r"\b([A-Z0-9][A-Z0-9'’&!:,.\-]*(?: [A-Z0-9'’&!:,.\-]+)+|[A-Z][A-Z'’&!\-]{3,})\b")
CAPS_STOP = {"UK", "USA", "CEO", "OBE", "MBE", "CBE", "BBC", "ITV", "NEW", "TOUR", "THE", "AND", "LIVE"}
ANNOUNCE = re.compile(r"\b(announce|announces|announced|presents|present|produc|co-produc)", re.I)


def show_of_page(text, owner_names=()):
    """The show a page announces: 'production of X' / 'season of X', or a title IN CAPITALS in an
    announcing sentence. The site owner's own name is never taken as a title. None if neither is found."""
    stop = CAPS_STOP | {w.upper() for n in owner_names for w in n.split()}
    for sent in sentences(text):
        if not ANNOUNCE.search(sent):
            continue
        m = OF_TITLE.search(sent)
        if m:
            return m.group("t").strip(), sent
        caps = [(c.group(1).strip(" ,.:"), c.end()) for c in CAPS_TITLE.finditer(sent)]
        caps = [c for c, end in caps if c.upper() == c and c not in stop and not all(w in stop for w in c.split())
                and not re.match(r" [A-Z][a-z]", sent[end:end + 3]) and not re.match(r" and (?:the )?\w*produc", sent[end:end + 20], re.I)]
        if caps:
            return max(caps, key=len), sent
    return None, None
