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
- United Agents casting directors: 8 page(s): https://www.unitedagents.co.uk/catriona-dickie-cdg/, https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/, https://www.unitedagents.co.uk/jill-trevellick-cdg/, https://www.unitedagents.co.uk/kate-dowd-cdg/, https://www.unitedagents.co.uk/louise-kiely-cdg/, https://www.unitedagents.co.uk/matthew-dewsbury-cdg/, https://www.unitedagents.co.uk/maya-kvetny-csa/, https://www.unitedagents.co.uk/stuart-
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
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BURLESQUE THE MUSICAL / 2026 / UK Tour / Casting Director / Dir. Robin Antin & Racky Plews

→ UK Tour **staged at** Burlesque The Musical

**Rule A1 matched (credit):**

> BURLESQUE THE MUSICAL / 2026 / UK Tour / Casting Director / Dir. Robin Antin & Racky Plews

→ Harry Blumenau **casting director** on Burlesque The Musical

**Identity:** source is their own agent's page.

## Example 3: Harry Blumenau, casting director on Burlesque The Musical

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BURLESQUE / 2025 / Savoy Theatre / Casting Director / Dir. Todrick Hall

→ Savoy Theatre **staged at** Burlesque The Musical

**Rule A1 matched (credit):**

> BURLESQUE / 2025 / Savoy Theatre / Casting Director / Dir. Todrick Hall

→ Harry Blumenau **casting director** on Burlesque The Musical

**Identity:** source is their own agent's page.

## Example 4: Harry Blumenau, casting director on Burlesque The Musical

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BURLESQUE / 2024 / Manchester Opera House/Theatre Royal Glasgow/Adama Entertainment / Casting Director / Dir. Nick Winston

→ Manchester Opera House/Theatre Royal Glasgow/Adama Entertainment **staged at** Burlesque The Musical

**Rule A1 matched (credit):**

> BURLESQUE / 2024 / Manchester Opera House/Theatre Royal Glasgow/Adama Entertainment / Casting Director / Dir. Nick Winston

→ Harry Blumenau **casting director** on Burlesque The Musical

**Identity:** source is their own agent's page.

## Example 5: Harry Blumenau, co-casting director on The Choir of Man

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> CHOIR OF MAN / 2022 / Arts Theatre / Co-Casting Director / Dir. Nic Doodson

→ Arts Theatre **staged at** The Choir of Man

**Rule A1 matched (credit):**

> CHOIR OF MAN / 2022 / Arts Theatre / Co-Casting Director / Dir. Nic Doodson

→ Harry Blumenau **casting director** on The Choir of Man

**Identity:** source is their own agent's page.

## Example 6: Harry Blumenau, casting director on Million Dollar Quartet

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> MILLION DOLLAR QUARTET / 2027 / UK Tour / Casting Director / Dir. Jonathan O’Boyle

→ UK Tour **staged at** Million Dollar Quartet

**Rule A1 matched (credit):**

> MILLION DOLLAR QUARTET / 2027 / UK Tour / Casting Director / Dir. Jonathan O’Boyle

→ Harry Blumenau **casting director** on Million Dollar Quartet

**Identity:** source is their own agent's page.

## Example 7: Harry Blumenau, casting director on In Pieces

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> IN PIECES / 2027 / The Other Palace / Casting Director / Dir. Martha Geelan

→ The Other Palace **staged at** In Pieces

**Rule A1 matched (credit):**

> IN PIECES / 2027 / The Other Palace / Casting Director / Dir. Martha Geelan

→ Harry Blumenau **casting director** on In Pieces

**Identity:** source is their own agent's page.

## Example 8: Harry Blumenau, casting director on The Radium Girls

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> THE RADIUM GIRLS / 2027 / Southwark Playhouse / Casting Director / Dir. Marissa Jaret Winokur

→ Southwark Playhouse **staged at** The Radium Girls

**Rule A1 matched (credit):**

> THE RADIUM GIRLS / 2027 / Southwark Playhouse / Casting Director / Dir. Marissa Jaret Winokur

→ Harry Blumenau **casting director** on The Radium Girls

**Identity:** source is their own agent's page.

## Example 9: Harry Blumenau, casting director on Legally Blonde

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> LEGALLY BLONDE / 2027 / London Coliseum / Casting Director / Dir. Nikolai Foster

→ London Coliseum **staged at** Legally Blonde

**Rule A1 matched (credit):**

> LEGALLY BLONDE / 2027 / London Coliseum / Casting Director / Dir. Nikolai Foster

→ Harry Blumenau **casting director** on Legally Blonde

**Identity:** source is their own agent's page.

## Example 10: Harry Blumenau, casting director on Nero

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> NERO / 2026 / Southwark Playhouse / Casting Director / Dir. Lindsay Posner

→ Southwark Playhouse **staged at** Nero

**Rule A1 matched (credit):**

> NERO / 2026 / Southwark Playhouse / Casting Director / Dir. Lindsay Posner

→ Harry Blumenau **casting director** on Nero

**Identity:** source is their own agent's page.

## Example 11: Harry Blumenau, casting director on Million Dollar Quartet

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> MILLION DOLLAR QUARTET / 2026 / Arts at Marble Arch/Barn Theatre / Casting Director / Dir. Jonathan O’Boyle

→ Arts at Marble Arch/Barn Theatre **staged at** Million Dollar Quartet

**Rule A1 matched (credit):**

> MILLION DOLLAR QUARTET / 2026 / Arts at Marble Arch/Barn Theatre / Casting Director / Dir. Jonathan O’Boyle

→ Harry Blumenau **casting director** on Million Dollar Quartet

**Identity:** source is their own agent's page.

## Example 12: Harry Blumenau, casting director on Dirty Dancing

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> DIRTY DANCING / 2026 / UK Tour / Casting Director / Dir. Frederico Bellone

→ UK Tour **staged at** Dirty Dancing

**Rule A1 matched (credit):**

> DIRTY DANCING / 2026 / UK Tour / Casting Director / Dir. Frederico Bellone

→ Harry Blumenau **casting director** on Dirty Dancing

**Identity:** source is their own agent's page.

## Example 13: Harry Blumenau, casting director on The Silence Of The Lambs

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> THE SILENCE OF THE LAMBS / 2026 / Leicester Curve/UK Tour / Casting Director / Dir. Nikolai Foster

→ Leicester Curve/UK Tour **staged at** The Silence Of The Lambs

**Rule A1 matched (credit):**

> THE SILENCE OF THE LAMBS / 2026 / Leicester Curve/UK Tour / Casting Director / Dir. Nikolai Foster

→ Harry Blumenau **casting director** on The Silence Of The Lambs

**Identity:** source is their own agent's page.

## Example 14: Harry Blumenau, casting director on Heated Rivalry: The Unauthorized Musical Parody

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> HEATED RIVALRY: THE UNAUTHORIZED MUSICAL PARODY / 2026 / Udderbelly/Underbelly Boulevard / Casting Director / Dir. Alan Kliffer

→ Udderbelly/Underbelly Boulevard **staged at** Heated Rivalry: The Unauthorized Musical Parody

**Rule A1 matched (credit):**

> HEATED RIVALRY: THE UNAUTHORIZED MUSICAL PARODY / 2026 / Udderbelly/Underbelly Boulevard / Casting Director / Dir. Alan Kliffer

→ Harry Blumenau **casting director** on Heated Rivalry: The Unauthorized Musical Parody

**Identity:** source is their own agent's page.

## Example 15: Harry Blumenau, casting director on Here Comes J. Edgar!

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> HERE COMES J. EDGAR! / 2026 / King's Head Theatre / Casting Director / Dir. Josh Seymour

→ King's Head Theatre **staged at** Here Comes J. Edgar!

**Rule A1 matched (credit):**

> HERE COMES J. EDGAR! / 2026 / King's Head Theatre / Casting Director / Dir. Josh Seymour

→ Harry Blumenau **casting director** on Here Comes J. Edgar!

**Identity:** source is their own agent's page.

## Example 16: Harry Blumenau, casting director on Beetlejuice The Musical

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BEETLEJUICE THE MUSICAL / 2026 / Prince Edward Theatre / Casting Director / Dir. Alex Timbers

→ Prince Edward Theatre **staged at** Beetlejuice The Musical

**Rule A1 matched (credit):**

> BEETLEJUICE THE MUSICAL / 2026 / Prince Edward Theatre / Casting Director / Dir. Alex Timbers

→ Harry Blumenau **casting director** on Beetlejuice The Musical

**Identity:** source is their own agent's page.

## Example 17: Harry Blumenau, casting director on Public: The Musical

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> PUBLIC: THE MUSICAL / 2026 / Leicester Curve / Casting Director / Dir. Hannah Sands

→ Leicester Curve **staged at** Public: The Musical

**Rule A1 matched (credit):**

> PUBLIC: THE MUSICAL / 2026 / Leicester Curve / Casting Director / Dir. Hannah Sands

→ Harry Blumenau **casting director** on Public: The Musical

**Identity:** source is their own agent's page.

## Example 18: Harry Blumenau, casting director on Bank Of Dave

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BANK OF DAVE / 2026 / Lowry Theatre/Leicester Curve / Casting Director / Dir. Nikolai Foster

→ Lowry Theatre/Leicester Curve **staged at** Bank Of Dave

**Rule A1 matched (credit):**

> BANK OF DAVE / 2026 / Lowry Theatre/Leicester Curve / Casting Director / Dir. Nikolai Foster

→ Harry Blumenau **casting director** on Bank Of Dave

**Identity:** source is their own agent's page.

## Example 19: Harry Blumenau, casting director on Kinky Boots

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> KINKY BOOTS / 2026 / London Coliseum / Casting Director / Dir. Nikolai Foster

→ London Coliseum **staged at** Kinky Boots

**Rule A1 matched (credit):**

> KINKY BOOTS / 2026 / London Coliseum / Casting Director / Dir. Nikolai Foster

→ Harry Blumenau **casting director** on Kinky Boots

**Identity:** source is their own agent's page.

## Example 20: Harry Blumenau, casting director on In Pieces: In Concert

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> IN PIECES: IN CONCERT / 2026 / The Other Palace / Casting Director / Dir. Martha Geelan

→ The Other Palace **staged at** In Pieces: In Concert

**Rule A1 matched (credit):**

> IN PIECES: IN CONCERT / 2026 / The Other Palace / Casting Director / Dir. Martha Geelan

→ Harry Blumenau **casting director** on In Pieces: In Concert

**Identity:** source is their own agent's page.

## Example 21: Harry Blumenau, casting director on Legally Blonde

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> LEGALLY BLONDE / 2026 / Leicester Curve/UK Tour / Casting Director / Dir. Nikolai Foster

→ Leicester Curve/UK Tour **staged at** Legally Blonde

**Rule A1 matched (credit):**

> LEGALLY BLONDE / 2026 / Leicester Curve/UK Tour / Casting Director / Dir. Nikolai Foster

→ Harry Blumenau **casting director** on Legally Blonde

**Identity:** source is their own agent's page.

## Example 22: Harry Blumenau, casting director on Rock & Roll Man

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> ROCK & ROLL MAN / 2026 / Salisbury Playhouse / Casting Director / Dir. Randal Myler

→ Salisbury Playhouse **staged at** Rock & Roll Man

**Rule A1 matched (credit):**

> ROCK & ROLL MAN / 2026 / Salisbury Playhouse / Casting Director / Dir. Randal Myler

→ Harry Blumenau **casting director** on Rock & Roll Man

**Identity:** source is their own agent's page.

## Example 23: Harry Blumenau, casting director on Beautiful Little Fool

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BEAUTIFUL LITTLE FOOL / 2026 / Southwark Playhouse / Casting Director / Dir. Michael Greif

→ Southwark Playhouse **staged at** Beautiful Little Fool

**Rule A1 matched (credit):**

> BEAUTIFUL LITTLE FOOL / 2026 / Southwark Playhouse / Casting Director / Dir. Michael Greif

→ Harry Blumenau **casting director** on Beautiful Little Fool

**Identity:** source is their own agent's page.

## Example 24: Harry Blumenau, casting director on Ride The Cyclone

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> RIDE THE CYCLONE / 2025 / Southwark Playhouse / Casting Director / Dir. Lizzi Gee

→ Southwark Playhouse **staged at** Ride The Cyclone

**Rule A1 matched (credit):**

> RIDE THE CYCLONE / 2025 / Southwark Playhouse / Casting Director / Dir. Lizzi Gee

→ Harry Blumenau **casting director** on Ride The Cyclone

**Identity:** source is their own agent's page.

## Example 25: Harry Blumenau, casting director on Midnight

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> MIDNIGHT / 2025 / Sadlers Wells: East / Casting Director / Dir. Todrick Hall

→ Sadlers Wells: East **staged at** Midnight

**Rule A1 matched (credit):**

> MIDNIGHT / 2025 / Sadlers Wells: East / Casting Director / Dir. Todrick Hall

→ Harry Blumenau **casting director** on Midnight

**Identity:** source is their own agent's page.

## Example 26: Harry Blumenau, casting director on Fanny

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> FANNY / 2025 / King's Head Theatre / Casting Director / Dir. Katie-Anne McDonough

→ King's Head Theatre **staged at** Fanny

**Rule A1 matched (credit):**

> FANNY / 2025 / King's Head Theatre / Casting Director / Dir. Katie-Anne McDonough

→ Harry Blumenau **casting director** on Fanny

**Identity:** source is their own agent's page.

## Example 27: Harry Blumenau, casting director on The Last Five Years

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> THE LAST FIVE YEARS / 2025 / Barn Theatre/Reading Rep / Casting Director / Dir. Hal Chambers

→ Barn Theatre/Reading Rep **staged at** The Last Five Years

**Rule A1 matched (credit):**

> THE LAST FIVE YEARS / 2025 / Barn Theatre/Reading Rep / Casting Director / Dir. Hal Chambers

→ Harry Blumenau **casting director** on The Last Five Years

**Identity:** source is their own agent's page.

## Example 28: Harry Blumenau, children’s’ casting director on Evita

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> EVITA / 2025 / London Palladium / Children’s’ Casting Director / Dir. Jamie Lloyd

→ London Palladium **staged at** Evita

**Rule A1 matched (credit):**

> EVITA / 2025 / London Palladium / Children’s’ Casting Director / Dir. Jamie Lloyd

→ Harry Blumenau **casting director** on Evita

**Identity:** source is their own agent's page.

## Example 29: Harry Blumenau, casting director on The Hunchback Of Notre Dame

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> THE HUNCHBACK OF NOTRE DAME / 2025 / Prince Edward Theatre / Casting Director / Dir. Jonathan O’Boyle

→ Prince Edward Theatre **staged at** The Hunchback Of Notre Dame

**Rule A1 matched (credit):**

> THE HUNCHBACK OF NOTRE DAME / 2025 / Prince Edward Theatre / Casting Director / Dir. Jonathan O’Boyle

→ Harry Blumenau **casting director** on The Hunchback Of Notre Dame

**Identity:** source is their own agent's page.

## Example 30: Harry Blumenau, casting director on Glorious!

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> GLORIOUS! / 2025 / Hope Mill Theatre / Casting Director / Dir. Kirk Jameson

→ Hope Mill Theatre **staged at** Glorious!

**Rule A1 matched (credit):**

> GLORIOUS! / 2025 / Hope Mill Theatre / Casting Director / Dir. Kirk Jameson

→ Harry Blumenau **casting director** on Glorious!

**Identity:** source is their own agent's page.

## Example 31: Harry Blumenau, casting director on Kinky Boots

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> KINKY BOOTS / 2025 / Leicester Curve/UK Tour / Casting Director / Dir. Nikolai Foster

→ Leicester Curve/UK Tour **staged at** Kinky Boots

**Rule A1 matched (credit):**

> KINKY BOOTS / 2025 / Leicester Curve/UK Tour / Casting Director / Dir. Nikolai Foster

→ Harry Blumenau **casting director** on Kinky Boots

**Identity:** source is their own agent's page.

## Example 32: Harry Blumenau, casting director on Scissorhandz

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> SCISSORHANDZ / 2025 / Southwark Playhouse / Casting Director / Dir. Bradley Bredeweg

→ Southwark Playhouse **staged at** Scissorhandz

**Rule A1 matched (credit):**

> SCISSORHANDZ / 2025 / Southwark Playhouse / Casting Director / Dir. Bradley Bredeweg

→ Harry Blumenau **casting director** on Scissorhandz

**Identity:** source is their own agent's page.

## Example 33: Harry Blumenau, casting director on Jack And The Beanstalk

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> JACK AND THE BEANSTALK / 2024 / Charing Cross Theatre / Casting Director / Dir. Andrew Beckett

→ Charing Cross Theatre **staged at** Jack And The Beanstalk

**Rule A1 matched (credit):**

> JACK AND THE BEANSTALK / 2024 / Charing Cross Theatre / Casting Director / Dir. Andrew Beckett

→ Harry Blumenau **casting director** on Jack And The Beanstalk

**Identity:** source is their own agent's page.

## Example 34: Harry Blumenau, casting director on Why Am I So Single?

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> WHY AM I SO SINGLE? / 2024 / Garrick Theatre/Kenny Wax Ltd/Ameena Hamid Productions / Casting Director / Dir. Lucy Moss & Ellen Kane

→ Garrick Theatre/Kenny Wax Ltd/Ameena Hamid Productions **staged at** Why Am I So Single?

**Rule A1 matched (credit):**

> WHY AM I SO SINGLE? / 2024 / Garrick Theatre/Kenny Wax Ltd/Ameena Hamid Productions / Casting Director / Dir. Lucy Moss & Ellen Kane

→ Harry Blumenau **casting director** on Why Am I So Single?

**Identity:** source is their own agent's page.

## Example 35: Harry Blumenau, casting director on Winghaven Park

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> WINGHAVEN PARK / 2024 / Thomas Hopkins Productions / Casting Director / Dir. Gabriel Barre

→ Thomas Hopkins Productions **staged at** Winghaven Park

**Rule A1 matched (credit):**

> WINGHAVEN PARK / 2024 / Thomas Hopkins Productions / Casting Director / Dir. Gabriel Barre

→ Harry Blumenau **casting director** on Winghaven Park

**Identity:** source is their own agent's page.

## Example 36: Harry Blumenau, casting director on Your Lie In April

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> YOUR LIE IN APRIL / 2024 / Harold Pinter Theatre/Carter Dixon McGill / Casting Director / Dir. Nick Winston

→ Harold Pinter Theatre/Carter Dixon McGill **staged at** Your Lie In April

**Rule A1 matched (staged at):**

> YOUR LIE IN APRIL / 2024 / Theatre Royal Drury Lane/Carter Dixon McGill / Casting Director / Dir. Nick Winston

→ Theatre Royal Drury Lane/Carter Dixon McGill **staged at** Your Lie In April

**Rule A1 matched (credit):**

> YOUR LIE IN APRIL / 2024 / Harold Pinter Theatre/Carter Dixon McGill / Casting Director / Dir. Nick Winston

→ Harry Blumenau **casting director** on Your Lie In April

**Identity:** source is their own agent's page.

## Example 37: Harry Blumenau, casting director on Blippi: The Wonderful World Tour

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BLIPPI: THE WONDERFUL WORLD TOUR / 2024 / Harold Pinter Theatre/Carter Dixon McGill / Casting Director / Dir. Simon Greiff

→ Harold Pinter Theatre/Carter Dixon McGill **staged at** Blippi: The Wonderful World Tour

**Rule A1 matched (credit):**

> BLIPPI: THE WONDERFUL WORLD TOUR / 2024 / Harold Pinter Theatre/Carter Dixon McGill / Casting Director / Dir. Simon Greiff

→ Harry Blumenau **casting director** on Blippi: The Wonderful World Tour

**Identity:** source is their own agent's page.

## Example 38: Harry Blumenau, casting director on Babies

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> BABIES / 2024 / The Other Palace / Casting Director / Dir. Martha Geelan

→ The Other Palace **staged at** Babies

**Rule A1 matched (credit):**

> BABIES / 2024 / The Other Palace / Casting Director / Dir. Martha Geelan

→ Harry Blumenau **casting director** on Babies

**Identity:** source is their own agent's page.

## Example 39: Harry Blumenau, casting director on Fanny

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> FANNY / 2024 / Watermill Theatre / Casting Director / Dir. Katie-Ann McDonough

→ Watermill Theatre **staged at** Fanny

**Rule A1 matched (credit):**

> FANNY / 2024 / Watermill Theatre / Casting Director / Dir. Katie-Ann McDonough

→ Harry Blumenau **casting director** on Fanny

**Identity:** source is their own agent's page.

## Example 40: Harry Blumenau, revival casting director on My Beautiful Laundrette

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> MY BEAUTIFUL LAUNDRETTE / 2024 / Leicester Curve/UK Tour / Revival Casting Director / Dir. Nicole Behan

→ Leicester Curve/UK Tour **staged at** My Beautiful Laundrette

**Rule A1 matched (credit):**

> MY BEAUTIFUL LAUNDRETTE / 2024 / Leicester Curve/UK Tour / Revival Casting Director / Dir. Nicole Behan

→ Harry Blumenau **casting director** on My Beautiful Laundrette

**Identity:** source is their own agent's page.

## Example 41: Harry Blumenau, casting director on Wild About You

**Page:** https://www.unitedagents.co.uk/harry-blumenau-cdg-csa/  
**Fetched:** 2026-11-17T08:51:19Z · **SHA-256:** `01dcb8b5445f6dbb30d17bc165c50addae4a924e9651fe115f132fc4d68eecce`

**Rule A1 matched (staged at):**

> WILD ABOUT YOU / 2024 / Theatre Royal Drury Lane/Carter Dixon McGill / Casting Director / Dir. Nick Winston

→ Theatre Royal Drury Lane/Carter Dixon McGill **staged at** Wild About You

**Rule A1 matched (credit):**

> WILD ABOUT YOU / 2024 / Theatre Royal Drury Lane/Carter Dixon McGill / Casting Director / Dir. Nick Winston

→ Harry Blumenau **casting director** on Wild About You

**Identity:** source is their own agent's page.

## Coverage

- Productions: 44 · People: 40 · Organisations: 26
- Credits: 93 (41 casting), of which 41 have identity confirmed
- Producer pages with no production sentence the rules know: 116
- Producer pages where the title couldn't be read: 20
- Official show-site pages with no credits written as text: 6

Nothing is guessed: every page the rules couldn't read is listed in graph.json under `coverage`.
