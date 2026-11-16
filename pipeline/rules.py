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

PRODUCER_SENTENCE = re.compile(r"Crossroads Live[^.]{0,120}\b(announce|announces|announced|presents|present|produc|co-produc)|"
                               r"\b(produced|presented|co-produced) by [^.]{0,80}Crossroads Live|for Crossroads Live", re.I)
CAPS_TITLE = re.compile(r"\b([A-Z0-9][A-Z0-9'’&!:,.\-]*(?: [A-Z0-9'’&!:,.\-]+)+|[A-Z][A-Z'’&!\-]{3,})\b")
CAPS_STOP = {"UK", "USA", "CEO", "OBE", "MBE", "CBE", "BBC", "ITV", "NEW", "TOUR", "THE", "AND", "LIVE", "CROSSROADS", "DAVID", "IAN"}
OF_TITLE = re.compile(r"production of (?:the )?(?:musical |hit musical |classic )?(?P<t>(?:[A-Z][\w'’&!:\-]*)(?: (?:of|the|and|in|a|to|on|[A-Z][\w'’&!:\-]*))*)")


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


def production(text):
    """Return (rule_id, title, sentence) for the production Crossroads Live announces, or None.
    Only the first producer sentence is used; a page naming several shows yields its first, and the
    coverage report lists pages where the title couldn't be read."""
    for sent in sentences(text):
        if not PRODUCER_SENTENCE.search(sent):
            continue
        caps = [c.strip(" ,.:") for c in CAPS_TITLE.findall(sent)]
        caps = [c for c in caps if c.upper() == c and c not in CAPS_STOP and not all(w in CAPS_STOP for w in c.split())]
        if caps:
            return ("P1", max(caps, key=len), sent)
        m = OF_TITLE.search(sent)
        if m:
            return ("P2", m.group("t").strip(), sent)
        return ("P0", None, sent)
    return None


# ---- A1: agency CV layout (United Agents uses it for every client) ----
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
