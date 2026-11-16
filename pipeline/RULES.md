# Rules used by the no-AI pipeline

Every connection in the network was made by one of these rules matching text that is really on a page.
No AI is used anywhere. Names of producers, people and sites live only in `seeds.json`, entered by a person.

## Production rules (producer press pages)

The producer's names come from its seed (`aliases`). Names in `ignore_in_titles` are never read as a show title.

| ID | Matches | Example |
|---|---|---|
| P2 | (tried first) A producer sentence with a capitalised title right after "production of" | "…a new production of The Wizard of Oz" |
| P1 | A producer sentence with the show title IN CAPITALS. Capitals followed by a capitalised word ("ARDA Studio") are a name, not a title | "David Ian for Crossroads Live is delighted to announce a new production of … CHITTY CHITTY BANG BANG" |

A **producer sentence** is one where the verb (announce, present, produce, co-produce) sits right next to the producer's name ("X is delighted to announce", "X presents", "produced by … X", "for X"), never across a semicolon or a second "by". So "general management by X; … executive produced by Y" does not count as X producing.
| P0 | A producer sentence where no title could be read. Nothing is created; the page is listed under coverage. | |

## Credit rules (any page)

| ID | Role | Matches |
|---|---|---|
| C1 | Casting director | "casting by NAME" |
| C2 | Casting director | "Casting Director NAME" / "Casting Director: NAME" |
| C3 | Director | "directed by NAME" |
| C4 | Director | "Director: NAME" |
| C5 | Choreographer | "choreography by NAME" / "choreographed by NAME" |
| C6 | Writer | "written by NAME" / "book by NAME" |

A credit is **not** taken when the role has a qualifier in front of it (Associate, Assistant, Resident, Fight, Intimacy, Movement, Musical, Artistic, Video, Lighting, Sound, Co-, Deputy, Executive, Creative, Production, Technical, Puppetry, Voice, Dialect, Children's), or when the "name" contains words that show it isn't a person (Director, Theatre, Productions, Live, Company, Ltd, Group, Entertainment, Award, Tour, Musical, Season, West End, Broadway, London, UK, or a possessive like "Curve's").

A NAME is 2–4 capitalised words on one line (with "de", "van", "von", "di" allowed). Several names joined by "and", "&" or commas give several credits.

## Layout rules (chosen by site)

| ID | Site | Layout |
|---|---|---|
| A1 | unitedagents.co.uk | A client CV: TITLE IN CAPITALS / year / venue or company / role / "Dir. Name & Name". Gives the client's credit, the director credits and the venue. |

## Identity

- **Confirmed by own site:** the person's own website (a `person-site` seed) also names the same show.
- **Source is their own agent's page:** the credit comes from the person's agency CV.
- **Name match only:** everything else. People are never merged on similar names.

Show titles are matched after removing "The" at the start, "(The) Musical" at the end, case and punctuation.

## General lists (not tied to any site)

- **Title words never read as a show title:** UK, USA, CEO, OBE, MBE, CBE, BBC, ITV, NEW, TOUR, THE, AND, LIVE.
- **AI crawlers checked in robots.txt (reported only):** ClaudeBot, anthropic-ai, GPTBot, CCBot, Google-Extended, Bytespider, PerplexityBot, Applebot-Extended.
- **Words flagged in terms pages for a person to read:** scrape, crawl, robot, spider, automated, data mining, harvest, extract, systematic, reproduce, republish, database.
