# Trace: how one connection is made with no AI

## Step 1. Source check (check_sources.py)

- Crossroads Live robots.txt: HTTP 200, our agent allowed: True, `/press/` allowed: True
- AI crawlers it blocks: ClaudeBot, anthropic-ai, GPTBot, CCBot, Google-Extended, Bytespider, Applebot-Extended
- Debbie O'Brien Casting robots.txt: HTTP 200, our agent allowed: True

## Step 2. Fetch (fetch.py)

- Crossroads Live: 14 press pages fetched from its own sitemap.
- Debbie O'Brien Casting: 6 pages fetched.

## Example 1: Debbie O'Brien, casting director on CHITTY CHITTY BANG BANG

**Page:** https://www.xroadslive.com/press/the-most-fantasmagorical-musical-of-all-time-is-back-for-a-uk-tour-in-2024  
**Fetched:** 2026-11-16T23:09:38Z · **SHA-256:** `b5b9d26e3a70f6373182eeff48544289df36bb0fabb0169fe4dcb36685b0814a`

**Step 3a. Rule P1 (production) matched:**

> David Ian for Crossroads Live is delighted to announce a new production of the most fantasmagorical musical of all time, CHITTY CHITTY BANG BANG, opening at Mayflower Theatre, Southampton on 30 April 2024 where it will play until 12 May 2024 ahead of a UK tour.

→ connection: Crossroads Live **produces** CHITTY CHITTY BANG BANG

**Step 3b. Rule C1 (credit) matched:**

> This new production will be directed by Thom Southerland (Titanic, Parade), choreographed by Karen Bruce (BBC's Strictly Come Dancing, The Bodyguard) with Set and Costume design by Morgan Large (Newsies, Joseph and the Technicolour Dreamcoat), Orchestrations and Musical Supervision by George Dyer (The Wizard of Oz, Annie, Billy Elliot)and casting by Debbie O'Brien.

→ connection: Debbie O'Brien **casting director** on CHITTY CHITTY BANG BANG

**Step 4. Identity:** confirmed by own site. Her own site (debbieobrien.net) says:

> West End productions include: Thriller Live, The Knowledge, Annie (children’s casting), Kinky Boots (children’s casting), Close to You, Sinatra, American Idiot, Dusty, The Bodyguard (children’s casting), Show Boat (children’s casting), In the Bar of a Tokyo Hotel, Priscilla Queen of the Desert, Grease, Flashdance, Piaf, The Snowman, Respect La Diva, The King and I, The Harder They Come, Showboat, Dancing in the Streets, The Rat Pack Live from Las Vegas, Chitty Chitty Bang Bang, Saturday Night Fever, Fame, Peter Pan, The Pirates of Penzance, Mum’s the Word, Daisy Pulls It Off, Napoleon, Madame Melville, Hedwig and the Angry Inch, La Cava, Smokey Joe's Café, The Rocky Horror Show, Soul Train, Rent, Always, Steaming, Ain't Misbehavin', Disgracefully Yours.

## Whole archive

- Productions found: 3
- People found: 5
- Credits found: 5 (1 casting)
- Pages with no Crossroads Live production sentence: 8
- Pages where a production sentence was found but no title could be read: 3
- Pages with a production but no credit matched: 1

Nothing is guessed: pages the rules can't read are listed in graph.json under `coverage`, so a person can see what was missed.
