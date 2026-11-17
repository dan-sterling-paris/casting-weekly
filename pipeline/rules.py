"""Step 3. Fixed pattern rules. Each rule has an ID; every match keeps the exact sentence it came from.
No AI: the same text always gives the same matches."""
import re

NAME = r"[A-Z][A-Za-z'’\-]+(?: (?:de|van|von|di|[A-Z][A-Za-z'’\-]+)){1,3}"
NAMES = r"(?P<names>" + NAME + r"(?:(?:,| and| &) " + NAME + r")*)"
QUALIFIERS = r"(Associate|Assistant|Resident|Fight|Intimacy|Movement|Musical|Music|Artistic|Video|Lighting|Sound|Co-|Deputy|Executive|Creative|Production|Technical|Puppetry|Voice|Dialect|Children's|Children’s)"

CREDIT_RULES = [
    ("C1", "Casting director", re.compile(r"\b[Cc]asting by " + NAMES)),
    ("C2", "Casting director", re.compile(r"(?<!" + "Associate " + r")(?<!Assistant )\bCasting Director(?:s)?[,:]? " + NAMES)),
    ("C3", "Director", re.compile(r"\b[Dd]irected by " + NAMES)),
    ("C4", "Director", re.compile(r"(?<![A-Za-z’'-] )(?<!\w)Director[,:] " + NAMES)),
    ("C5", "Choreographer", re.compile(r"\b(?:[Cc]horeography by|[Cc]horeographed by) " + NAMES)),
    ("C6", "Writer", re.compile(r"\b(?:[Ww]ritten by|[Bb]ook by) " + NAMES)),
]
QUAL_BEFORE = re.compile(QUALIFIERS + r"\s*(?:&\s*\w+\s*)?$", re.I)
NOT_A_NAME = re.compile(r"'s\b|’s\b|\b(Director|Artistic|Associate|Producer|Chief|Executive|Theatre|Productions?|Live|Company|Ltd|Limited|Group|Entertainment|Award|Awards|Tour|Musical|Season|West End|Broadway|London|UK)\b")

PRODUCER_VERBS = r"(announce|announces|announced|presents|present|produc|co-produc)"


def producer_sentence(names):
    """Build the producer-sentence pattern from the producer names a person entered in seeds.json."""
    alt = "|".join(re.escape(n) for n in names)
    # the verb must sit next to the producer's name, without crossing ';' (credit lists use ';' between roles)
    return re.compile(r"(?:%s)(?: (?:is|are))?(?: (?:delighted|thrilled|pleased|proud|excited))?(?: to)? \b%s|"
                      r"\b(?:produced|presented|co-produced) by (?:(?!\bby\b)[^.;]){0,60}(?:%s)|\bfor (?:%s)\b" % (alt, PRODUCER_VERBS, alt, alt), re.I)


CAPS_TITLE = re.compile(r"\b([A-Z0-9][A-Z0-9'’&!:,.\-]*(?: [A-Z0-9'’&!:,.\-]+)+|[A-Z][A-Z'’&!\-]{3,})\b")
CAPS_STOP = {"UK", "USA", "CEO", "OBE", "MBE", "CBE", "BBC", "ITV", "NEW", "TOUR", "THE", "AND", "LIVE"}  # general words only
OF_TITLE = re.compile(r"(?:production|season) of (?:the )?(?:musical |hit musical |classic )?(?P<t>(?:[A-Z][\w'’&!:\-]*)(?: (?:of|the|and|in|a|to|on|\+|&|[A-Z][\w'’&!:\-]*))*)")


def sentences(text):
    out = []
    for line in text.split("\n"):
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z“\"])", line):
            s = s.strip()
            if len(s) > 3:
                out.append(s)
    return out


def split_names(s):
    return [n.strip() for n in re.split(r",| and | & ", s) if n.strip()]


def credits(text):
    """Return [(rule_id, role, name, sentence)]."""
    found = []
    for sent in sentences(text):
        for rid, role, rx in CREDIT_RULES:
            for m in rx.finditer(sent):
                if QUAL_BEFORE.search(sent[:m.start()]):
                    continue
                for n in split_names(m.group("names")):
                    if NOT_A_NAME.search(n):
                        continue
                    found.append((rid, role, n, sent))
    return found


def production(text, producer_names, ignore_in_titles=()):
    """Return (rule_id, title, sentence) for the production the producer announces, or None.
    producer_names and ignore_in_titles come from the producer's seed (entered by a person).
    Only the first producer sentence is used; pages where the title couldn't be read are listed in coverage."""
    rx = producer_sentence(producer_names)
    stop = CAPS_STOP | {w.upper() for x in list(producer_names) + list(ignore_in_titles) for w in x.split()}
    for sent in sentences(text):
        if not rx.search(sent):
            continue
        m = OF_TITLE.search(sent)
        if m:
            return ("P2", m.group("t").strip(), sent)
        # words in capitals followed by a capitalised word ("ARDA Studio") are a name, not a title
        caps = [(c.group(1).strip(" ,.:"), c.end()) for c in CAPS_TITLE.finditer(sent)]
        caps = [c for c, end in caps if c.upper() == c and c not in stop and not all(w in stop for w in c.split())
                and not re.match(r" [A-Z][a-z]", sent[end:end + 3])
                and not re.match(r" and (?:the )?\w*produc", sent[end:end + 20], re.I)]  # "X and producers ..." = an organisation
        if caps:
            return ("P1", max(caps, key=len), sent)
        return ("P0", None, sent)
    return None


# ---- A1: an agency CV layout (one agency uses it for every client; see LAYOUTS) ----
#   TITLE IN CAPITALS / year or year range / venue or company / role / "Dir. Name & Name"
YEAR_LINE = re.compile(r"^(19|20)\d\d(\s*[–-]\s*(19|20)\d\d)?$")
CV_ROLE = re.compile(r"Casting Director|Director|Writer|Choreographer|Producer", re.I)


def agent_cv(text):
    """Return one dict per credit block in an agency CV page laid out as above."""
    lines = [l.strip() for l in text.split("\n")]
    out = []
    for i in range(len(lines) - 4):
        title, year, venue, role, dirl = lines[i:i + 5]
        if not (title and title.upper() == title and re.search(r"[A-Z]{2}", title) and YEAR_LINE.match(year)
                and venue and CV_ROLE.search(role) and dirl.startswith("Dir. ")):
            continue
        directors = [n.strip() for n in re.split(r",| & | and ", dirl[5:]) if n.strip()]
        out.append({"title": title, "year": year, "venue": venue, "role": role, "directors": directors,
                    "evidence": " / ".join([title, year, venue, role, dirl])})
    return out


# Layout rules are chosen by site. Each entry is (rule ID, function); add a line here for each new layout.
LAYOUTS = {
    "unitedagents.co.uk": ("A1", agent_cv),
}


# ---- G1: role label next to a name, on any site (no per-site rule needed) ----
# A line that is exactly a role label, next to a line that is only a name, is a credit.
# Lines naming other jobs ("Associate Director", "Lighting Designer") are recognised so they keep the
# pairing in step, but give no credit. A page must use one orientation throughout (name then role,
# or role then name); a page that mixes them gives nothing and is listed instead.
G1_ROLES = {
    "casting director": "Casting director", "casting directors": "Casting director", "casting": "Casting director", "casting by": "Casting director",
    "director": "Director", "directors": "Director", "directed by": "Director",
    "writer": "Writer", "writers": "Writer", "written by": "Writer", "playwright": "Writer", "book": "Writer", "book by": "Writer",
    "choreographer": "Choreographer", "choreography": "Choreographer", "choreography by": "Choreographer",
    "composer": "Composer", "music by": "Composer",
}
OTHER_JOB = re.compile(r"^(?:[A-Z][\w'’&/-]*\s?){0,4}(Director|Designer|Supervisor|Manager|Producer|Assistant|Associate|Arranger|Orchestrator|"
                       r"Orchestrations|Captain|Coach|Consultant|Lyricist|Lyrics|Dramaturg|Choreographer|Writer|Composer|Casting|Illusions|Puppetry|Swing|Understudy|Administrator|Administration)s?\b.*$")
VENUE_WORDS = re.compile(r"\b(Playhouse|Palace|Theatre|Theater|Hall|House|Centre|Center|Coliseum|Studios?|Arena|Pavilion|Opera|Arts|Rep|Lyceum|Festival|Tour|Productions?)\b")
NAME_LINE = re.compile(r"^(?P<names>" + NAME + r"(?:(?:,| and| &) " + NAME + r")*)(?: (?:CDG|CSA))*$")


def _kind(line):
    key = line.strip().rstrip(":").strip().lower()
    if key in G1_ROLES:
        return ("role", G1_ROLES[key])
    if OTHER_JOB.match(line.strip()):
        return ("other", None)
    m = NAME_LINE.match(line.strip())
    if m and not NOT_A_NAME.search(m.group("names")) and not VENUE_WORDS.search(m.group("names")):
        return ("name", m.group("names"))
    return (None, None)


def label_pairs(text):
    """Return (credits, status). credits: [(rule, role, name, evidence)]. status: 'ok', 'none' or 'mixed'."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    kinds = [_kind(l) for l in lines]
    runs, cur = [], []
    for i, (k, v) in enumerate(kinds):
        is_label = k in ("role", "other")
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
                    out.append(("G1", kinds[lab][1], n, lines[a] + " / " + lines[b]))
    return out, "ok"
