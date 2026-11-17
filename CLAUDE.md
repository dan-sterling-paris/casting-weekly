# Casting Weekly

## Looking up productions (pipeline/)

`pipeline/productions.txt` is a queue. Each show is researched once. When asked to run the lookup, or when the
scheduled "Casting Weekly lookup" message arrives:

1. `git pull --no-edit origin claude/adoring-babbage-p2ckfa` so Dan's GitHub edits to the queue are included.
2. Run `python3 pipeline/todo.py`. Look up **only** the show lines it prints (lines starting `#` are notes).
   If it prints "Nothing new to look up", stop: no lookup, no publish, no notification.
   How many it prints is `shows_per_run` in `pipeline/settings.json`.
3. Run the `production-credits-lookup` skill on those lines. Save its JSON unchanged as `pipeline/lookups/<YYYY-MM-DD>-<n>.json`.
4. Run `python3 pipeline/todo.py done <that json file name> "<line>" ...` with the lines exactly as printed.
   This moves them from the queue to `pipeline/lookups/done.txt`.
5. Run `pip install -q -r pipeline/requirements.txt` (Splink; once per container), then
   `python3 pipeline/check_lookups.py && python3 pipeline/match_names.py && python3 pipeline/extract.py`.
   `check_lookups.py` keeps only credits their cited page confirms (the rest go to `pipeline/out/unconfirmed.json`);
   `match_names.py` uses Splink to merge spellings of one person (`pipeline/out/names.json`; Dan's
   `pipeline/name_rules.txt` with `same:` / `different:` lines overrides it); `extract.py` builds `site/artifact.html`
   (the artifact) and `site/index.html` (the standalone page for castingweekly.com/site/).
6. Commit and push to `claude/adoring-babbage-p2ckfa`. If the push is rejected, `git pull --no-edit` and push again. Never force-push.
7. Publish `site/artifact.html` with the Artifact tool to https://claude.ai/artifact/VeDkFx2Y9h3ykZVb2c8quL
   (same URL; read it first if this conversation hasn't published it). The site's own text must not mention
   crawling, scraping or AI.
8. On a scheduled run, send one PushNotification (under 200 characters): shows looked up, credits kept/rejected,
   casting director(s) found or "casting not stated", any credit resting on a single page, and any new name merge or review.

## Corrections and takedowns

The site's takedown page stores requests from signed-in visitors in the artifact's database (collection `takedowns`,
one document per sender with a `requests` subcollection); others email privacy@castingweekly.com. When Dan grants one,
add `remove: <name>` or `remove: <name> | <show>` to `pipeline/name_rules.txt`, run `python3 pipeline/extract.py`,
commit, push and republish. The castingweekly.com copy updates only when the branch is pushed to `main`. The person or credit stays off the site on every later run.

Never research a line already in `done.txt`. To redo a show, Dan deletes its line from `done.txt` and adds it to the queue.
