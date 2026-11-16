# Trace: how connections are made with no AI

## Step 1. Source checks (check_sources.py)

- **Crossroads Live**: robots.txt HTTP 200, our agent allowed: yes; blocks AI crawlers: ClaudeBot, anthropic-ai, GPTBot, CCBot, Google-Extended, Bytespider, Applebot-Extended
- **Debbie O'Brien Casting**: robots.txt HTTP 200, our agent allowed: yes
- **The Choir of Man (official site)**: robots.txt HTTP 200, our agent allowed: yes
- **Burlesque The Musical (official site)**: robots.txt HTTP 404, our agent allowed: yes
- **Harry Blumenau (United Agents profile)**: robots.txt HTTP 200, our agent allowed: yes

## Step 2. Fetch (fetch.py)

- Crossroads Live: 14 page(s): https://www.xroadslive.com/press/beetlejuice-its-showtime-london, https://www.xroadslive.com/press/christmas-comes-early-at-the-crossroads-pantomimes, https://www.xroadslive.com/press/dead-special-beetlejuice-opens-in-the-west-end, https://www.xroadslive.com/press/everybody-say-yeah-kinky-boots-is-returning-to-chinanbsp, https://www.xroadslive.com/press/full-west-end-cast-announced-for-beetlejuice
- Debbie O'Brien Casting: 6 page(s): https://www.debbieobrien.net/bodyguard.html, https://www.debbieobrien.net/cc.html, https://www.debbieobrien.net/debbie-obrien.html, https://www.debbieobrien.net/fabulist.html, https://www.debbieobrien.net/ncl-june.html, https://www.debbieobrien.net/ptp-foh.html
- The Choir of Man (official site): 1 page(s): https://thechoirofman.com
- Burlesque The Musical (official site): 5 page(s): https://www.burlesqueonstage.com/, https://www.burlesqueonstage.com/cast, https://www.burlesqueonstage.com/faqs, https://www.burlesqueonstage.com/media-gallery, https://www.burlesqueonstage.com/sign-up
- Harry Blumenau (United Agents profile): 1 page(s): https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/
- Redirect: https://www.burlesquethemusical.com/ went to https://www.burlesqueonstage.com/; that site's robots.txt (HTTP 200) allows our agent.

## Example 1: Harry Blumenau, casting director on Burlesque The Musical

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-16T23:42:27Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BURLESQUE THE MUSICAL / 2026 / UK Tour / Casting Director / Dir. Robin Antin & Racky Plews

→ UK Tour **staged at** Burlesque The Musical

**Rule A1 matched (credit):**

> BURLESQUE THE MUSICAL / 2026 / UK Tour / Casting Director / Dir. Robin Antin & Racky Plews

→ Harry Blumenau **casting director** on Burlesque The Musical

**Identity:** source is their own agent's page.

## Example 2: Harry Blumenau, casting director on Burlesque The Musical

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-16T23:42:27Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BURLESQUE / 2025 / Savoy Theatre / Casting Director / Dir. Todrick Hall

→ Savoy Theatre **staged at** Burlesque The Musical

**Rule A1 matched (credit):**

> BURLESQUE / 2025 / Savoy Theatre / Casting Director / Dir. Todrick Hall

→ Harry Blumenau **casting director** on Burlesque The Musical

**Identity:** source is their own agent's page.

## Example 3: Harry Blumenau, casting director on Burlesque The Musical

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-16T23:42:27Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BURLESQUE / 2024 / Manchester Opera House/Theatre Royal Glasgow/Adama Entertainment / Casting Director / Dir. Nick Winston

→ Manchester Opera House/Theatre Royal Glasgow/Adama Entertainment **staged at** Burlesque The Musical

**Rule A1 matched (credit):**

> BURLESQUE / 2024 / Manchester Opera House/Theatre Royal Glasgow/Adama Entertainment / Casting Director / Dir. Nick Winston

→ Harry Blumenau **casting director** on Burlesque The Musical

**Identity:** source is their own agent's page.

## Example 4: Harry Blumenau, co-casting director on The Choir of Man

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-16T23:42:27Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> CHOIR OF MAN / 2022 / Arts Theatre / Co-Casting Director / Dir. Nic Doodson

→ Arts Theatre **staged at** The Choir of Man

**Rule A1 matched (credit):**

> CHOIR OF MAN / 2022 / Arts Theatre / Co-Casting Director / Dir. Nic Doodson

→ Harry Blumenau **casting director** on The Choir of Man

**Identity:** source is their own agent's page.

## Coverage

- Productions: 2 · People: 6 · Organisations: 4
- Credits: 9 (4 casting), of which 4 have identity confirmed
- Producer pages with no production sentence the rules know: 13
- Producer pages where the title couldn't be read: 1
- Official show-site pages with no credits written as text: 6

Nothing is guessed: every page the rules couldn't read is listed in graph.json under `coverage`.
