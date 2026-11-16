"""Step 4. Deterministic identity: people are keyed by normalised name, never merged on similarity.
A person is 'confirmed' for a production when their own website also names that production."""
import re
import unicodedata


def norm(s):
    s = unicodedata.normalize("NFKC", s).replace("’", "'").replace("‘", "'")
    s = re.sub(r"\s+(CDG|CSA)\b", "", s)
    return re.sub(r"\s+", " ", s).strip().casefold()


def norm_title(s):
    s = unicodedata.normalize("NFKC", s).replace("’", "'").casefold()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def confirm(title, own_site_text):
    """Return the line of the person's own site that names the title, or None."""
    t = norm_title(title)
    if not t:
        return None
    for line in own_site_text.split("\n"):
        if re.search(r"\b" + re.escape(t) + r"\b", norm_title(line)):
            return line.strip()
    return None
