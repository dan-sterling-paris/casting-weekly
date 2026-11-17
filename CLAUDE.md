# Casting Weekly

## Looking up productions (pipeline/)

Each show is researched once. When asked to run the lookup:

1. Run `python3 pipeline/todo.py`. Look up **only** the lines it prints. If it prints "Nothing new to look up", stop.
2. Run the `production-credits-lookup` skill on those lines. Save its JSON unchanged as `pipeline/lookups/<YYYY-MM-DD>-<n>.json`.
3. Append each line looked up, copied exactly from `pipeline/productions.txt`, to `pipeline/lookups/done.txt` as
   `<line>  →  <json file name>`.
4. Run `python3 pipeline/check_lookups.py && python3 pipeline/extract.py`, then report kept and rejected counts.

Never research a line already in `done.txt`. To redo a show, Dan deletes its line from `done.txt`.
