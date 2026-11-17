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


VERB_TAIL = re.compile(r"(\s+(Directed|Written|Choreographed|Produced|Designed|Composed|Starring|With))+$")


def split_names(s):
    names = [VERB_TAIL.sub("", re.sub(r"(\s+(CDG|CSA))+$", "", n.strip())) for n in re.split(r",| and | & ", s) if n.strip()]
    return [n for n in names if len(n.split()) >= 2]


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
        if re.search(r"\bbased on\b|\b(the|original) (film|movie)\b", sent, re.I):
            continue   # about the source material, not this production
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
    # Direction is decided once per page, only by clear evidence: a role line with a name on one side and
    # something else on the other. All such lines must agree; with no evidence, or evidence both ways,
    # nothing is taken from the page (missing is better than wrong).
    votes = set()
    for i, (k, _) in enumerate(kinds):
        if k not in ("role", "other"):
            continue
        prev_name = i > 0 and kinds[i - 1][0] == "name"
        next_name = i + 1 < len(kinds) and kinds[i + 1][0] == "name"
        if prev_name and not next_name:
            votes.add("name-first")
        elif next_name and not prev_name:
            votes.add("role-first")
    if not votes:
        return [], "none"
    if len(votes) > 1:
        return [], "mixed"
    role_first = votes.pop() == "role-first"
    out = []
    for r in runs:
        if (kinds[r[0]][0] == "name") == role_first:   # line the pairs up from the right first line
            r = r[1:]
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


NEWSY = re.compile(r"\b(announce[sd]?|announcing|cast|casting|tickets?|opens?|returns?|joins?|news|on sale|tour|premiere|extends?|celebrates?)\b", re.I)


def _words(s):
    return set(re.findall(r"[a-z0-9]+", s.lower().replace("’", "'"))) - {"the", "a", "an", "of", "and", "musical"}


def show_of_page(text, owner_names=(), page_title="", page_url=""):
    """The show a page is about.
    1. A show named in an announcing sentence ('production of X', 'season of X', or a title IN CAPITALS)
       whose words also appear in the page's own address or title; shows that only appear elsewhere on
       the page (for example in a cast member's biography) are ignored.
    2. Otherwise the page's own short heading, when it is a line on the page and not a news headline.
    None if neither fits, and the page's credits are left unread."""
    stop = CAPS_STOP | {w.upper() for n in owner_names for w in n.split()}
    where = _words(page_url.replace("-", " ").replace("/", " ") + " " + page_title)
    for sent in sentences(text):
        if not ANNOUNCE.search(sent):
            continue
        cands = [m.group("t").strip() for m in OF_TITLE.finditer(sent)]
        caps = [(c.group(1).strip(" ,.:"), c.end()) for c in CAPS_TITLE.finditer(sent)]
        cands += [c for c, end in caps if c.upper() == c and any(len(w) >= 3 and w.isalpha() and w not in stop for w in re.findall(r"[A-Z']+", c)) and c not in stop
                  and not all(w in stop for w in c.split()) and not re.match(r" [A-Z][a-z]", sent[end:end + 3])
                  and not re.match(r" and (?:the )?\w*produc", sent[end:end + 20], re.I)]
        for c in cands:
            w = _words(c)
            if w and w <= where:
                return c, sent
    heading = re.split(r" [-|–—] ", page_title)[0].strip()
    lines = {l.strip() for l in text.split("\n")}
    slug = re.sub(r"[^a-z0-9]+", " ", page_url.rstrip("/").rsplit("/", 1)[-1].lower()).strip()
    if heading and heading in lines and _words(heading) and _words(heading) == _words(slug) \
            and len(heading.split()) <= 6 and not NEWSY.search(heading) and not re.search(r"\b(CDG|CSA)\b|[!?]", heading) \
            and not re.search(r"\b(confirms?|reveals?|revealed|extends?|gearing|calling|celebrating|final|complete|full)\b", heading, re.I):
        return heading, heading   # a show page: its address is the show's name
    return None, None
