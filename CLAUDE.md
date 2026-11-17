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
5. Run `python3 pipeline/check_lookups.py && python3 pipeline/extract.py`.
6. Commit and push to `claude/adoring-babbage-p2ckfa`. If the push is rejected, `git pull --no-edit` and push again. Never force-push.
7. Publish: copy `prototype/industry-intel.html` to the scratchpad as `network-proto.html` with the
   `<!doctype>…<head>` wrapper and `</body></html>` stripped, and publish it with the Artifact tool to
   https://claude.ai/artifact/VeDkFx2Y9h3ykZVb2c8quL (same URL; read it first if this conversation hasn't published it).
8. On a scheduled run, send one PushNotification (under 200 characters): shows looked up, credits kept/rejected,
   casting director(s) found or "casting not stated", and any credit resting on a single page.

Never research a line already in `done.txt`. To redo a show, Dan deletes its line from `done.txt` and adds it to the queue.
