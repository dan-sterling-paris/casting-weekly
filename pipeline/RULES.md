# How Casting Weekly reads pages (no AI)

**Scrape → text → patterns.** Pages are fetched politely (robots.txt obeyed) and saved as text in
`pipeline/pages/`. `python3 pipeline/extract.py` applies three patterns to that text. Anything that
matches none of them is listed in `out/NOT_READ.md` and never guessed.

## The three patterns (none is written for a particular site)

**S: sentence.** Inside a sentence: "casting by NAME", "Casting Director: NAME", "directed by NAME",
"Director: NAME", "choreography by NAME", "written by / book by NAME". Not taken when a qualifier comes
first (Associate, Assistant, Resident, Fight, Musical, Children's…).

**L: label next to a name.** A line that is exactly a role (Casting Director, Director, Writer,
Choreographer, Composer…) next to a line that is only a name, in either order. Other job titles
(Associate Director, Lighting Designer…) are recognised but give nothing. A page that uses both orders
gives nothing.

**B: credit block (CV pages).** A show title IN CAPITALS, then within five lines "Casting Director", with
only a year, a venue (after the year) or "Dir. NAME" in between. The casting credit belongs to the person
whose page it is (from the page title). A page needs at least three blocks to count as a CV.

## Which show a sentence or label credit belongs to

The page's own announcing sentence: "production of X" / "season of X", or a title IN CAPITALS in a
sentence that announces, presents or produces. If neither is there, the credits are listed as
"page doesn't say which show" and not used.

## Names

2–4 capitalised words; "and" / "&" join several names; CDG / CSA are dropped. Words like Theatre,
Productions, Playhouse, Hall, Tour are never treated as a person.

## K: checked lookup (uses Claude to find, a script to check)

Dan types production names into `pipeline/productions.txt`. The `production-credits-lookup` skill (Claude)
searches the web and saves its answer, unchanged, in `pipeline/lookups/`. Then `check_lookups.py`, which uses
no AI, opens each cited page itself (robots.txt obeyed) and keeps a credit only if that page's text contains
both the person's name and the show's name. "Unknown" adds nothing. "Conflicting" and anything not found on
the page are listed in `out/LOOKUP_REJECTED.md`. In the network these credits are labelled
"found by Claude lookup · name checked on page by script", never "no AI".

Each show is researched once. `productions.txt` is a queue: after a show is looked up, its line moves to
`lookups/done.txt`, so an empty queue means nothing is waiting. A show already in `done.txt` is removed from the
queue if added again. Cited pages are cached in `out/lookup_pages.json`, so re-running the check makes no web
requests for pages already read.
