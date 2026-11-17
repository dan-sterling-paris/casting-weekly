# Trace: how connections are made with no AI

## Step 1. Source checks (check_sources.py)

- **Crossroads Live**: robots.txt HTTP 200, our agent allowed: yes; blocks AI crawlers: ClaudeBot, anthropic-ai, GPTBot, CCBot, Google-Extended, Bytespider, Applebot-Extended
- **Debbie O'Brien Casting**: robots.txt HTTP 200, our agent allowed: yes
- **The Choir of Man (official site)**: robots.txt HTTP 200, our agent allowed: yes
- **Burlesque The Musical (official site)**: robots.txt HTTP 404, our agent allowed: yes
- **Harry Blumenau (United Agents profile)**: robots.txt HTTP 200, our agent allowed: yes

## Step 2. Fetch (fetch.py)

- Crossroads Live: 152 page(s): https://www.xroadslive.com/press/2021-uk-tour-of-multi-award-winning-chicago-announced, https://www.xroadslive.com/press/9-to-5-to-partner-with-dolly-partons-imagination-library, https://www.xroadslive.com/press/agatha-christies-breathtaking-masterpiece-and-then-there-were-none-to-tour-to-melbourne-and-sydney, https://www.xroadslive.com/press/andrew-lloyd-webbers-smash-hit-west-end-amp-broadway-mu
- Debbie O'Brien Casting: 46 page(s): https://www.debbieobrien.net/aida-paris.html, https://www.debbieobrien.net/aida-thanks.html, https://www.debbieobrien.net/aida.html, https://www.debbieobrien.net/antr.html, https://www.debbieobrien.net/archive-lnd.html, https://www.debbieobrien.net/archived-casting.html, https://www.debbieobrien.net/bodyguard.html, https://www.debbieobrien.net/btf.html, https://www.debbieobrien.net/cc.html, https:
- The Choir of Man (official site): 1 page(s): https://thechoirofman.com
- Burlesque The Musical (official site): 5 page(s): https://www.burlesqueonstage.com/, https://www.burlesqueonstage.com/cast, https://www.burlesqueonstage.com/faqs, https://www.burlesqueonstage.com/media-gallery, https://www.burlesqueonstage.com/sign-up
- Harry Blumenau (United Agents profile): 1 page(s): https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/
- Redirect: https://www.burlesquethemusical.com/ went to https://www.burlesqueonstage.com/; that site's robots.txt (HTTP 200) allows our agent.

## Example 1: Debbie O'Brien, casting director on CHITTY CHITTY BANG BANG

**Page:** https://www.xroadslive.com/press/the-most-fantasmagorical-musical-of-all-time-is-back-for-a-uk-tour-in-2024  
**Fetched:** 2026-11-17T08:40:41Z · **SHA-256:** `b5b9d26e3a70f6373182eeff48544289df36bb0fabb0169fe4dcb36685b0814a`

**Rule C1 matched (credit):**

> This new production will be directed by Thom Southerland (Titanic, Parade), choreographed by Karen Bruce (BBC's Strictly Come Dancing, The Bodyguard) with Set and Costume design by Morgan Large (Newsies, Joseph and the Technicolour Dreamcoat), Orchestrations and Musical Supervision by George Dyer (The Wizard of Oz, Annie, Billy Elliot)and casting by Debbie O'Brien.

→ Debbie O'Brien **casting director** on CHITTY CHITTY BANG BANG

**Identity:** confirmed by own site. Their own site says:

> West End productions include: Thriller Live, The Knowledge, Annie (children’s casting), Kinky Boots (children’s casting), Close to You, Sinatra, American Idiot, Dusty, The Bodyguard (children’s casting), Show Boat (children’s casting), In the Bar of a Tokyo Hotel, Priscilla Queen of the Desert, Grease, Flashdance, Piaf, The Snowman, Respect La Diva, The King and I, The Harder They Come, Showboat, Dancing in the Streets, The Rat Pack Live from Las Vegas, Chitty Chitty Bang Bang, Saturday Night Fever, Fame, Peter Pan, The Pirates of Penzance, Mum’s the Word, Daisy Pulls It Off, Napoleon, Madame Melville, Hedwig and the Angry Inch, La Cava, Smokey Joe's Café, The Rocky Horror Show, Soul Train, Rent, Always, Steaming, Ain't Misbehavin', Disgracefully Yours.

## Example 2: Harry Blumenau, casting director on Burlesque The Musical

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:45:54Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BURLESQUE THE MUSICAL / 2026 / UK Tour / Casting Director / Dir. Robin Antin & Racky Plews

→ UK Tour **staged at** Burlesque The Musical

**Rule A1 matched (credit):**

> BURLESQUE THE MUSICAL / 2026 / UK Tour / Casting Director / Dir. Robin Antin & Racky Plews

→ Harry Blumenau **casting director** on Burlesque The Musical

**Identity:** source is their own agent's page.

## Example 3: Harry Blumenau, casting director on Burlesque The Musical

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:45:54Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BURLESQUE / 2025 / Savoy Theatre / Casting Director / Dir. Todrick Hall

→ Savoy Theatre **staged at** Burlesque The Musical

**Rule A1 matched (credit):**

> BURLESQUE / 2025 / Savoy Theatre / Casting Director / Dir. Todrick Hall

→ Harry Blumenau **casting director** on Burlesque The Musical

**Identity:** source is their own agent's page.

## Example 4: Harry Blumenau, casting director on Burlesque The Musical

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:45:54Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BURLESQUE / 2024 / Manchester Opera House/Theatre Royal Glasgow/Adama Entertainment / Casting Director / Dir. Nick Winston

→ Manchester Opera House/Theatre Royal Glasgow/Adama Entertainment **staged at** Burlesque The Musical

**Rule A1 matched (credit):**

> BURLESQUE / 2024 / Manchester Opera House/Theatre Royal Glasgow/Adama Entertainment / Casting Director / Dir. Nick Winston

→ Harry Blumenau **casting director** on Burlesque The Musical

**Identity:** source is their own agent's page.

## Example 5: Harry Blumenau, co-casting director on The Choir of Man

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:45:54Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> CHOIR OF MAN / 2022 / Arts Theatre / Co-Casting Director / Dir. Nic Doodson

→ Arts Theatre **staged at** The Choir of Man

**Rule A1 matched (credit):**

> CHOIR OF MAN / 2022 / Arts Theatre / Co-Casting Director / Dir. Nic Doodson

→ Harry Blumenau **casting director** on The Choir of Man

**Identity:** source is their own agent's page.

## Coverage

- Productions: 12 · People: 16 · Organisations: 5
- Credits: 20 (5 casting), of which 5 have identity confirmed
- Producer pages with no production sentence the rules know: 116
- Producer pages where the title couldn't be read: 20
- Official show-site pages with no credits written as text: 6

Nothing is guessed: every page the rules couldn't read is listed in graph.json under `coverage`.
