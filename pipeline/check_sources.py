"""Step 1. Check each seed site: robots.txt for our agent, whether it blocks AI bots, and its terms.
Writes pipeline/out/sources.json and pipeline/out/sources.md. No AI involved."""
import json
import re
from common import AI_AGENTS, OUT, TERMS_RE, CLAUSE_RE, UA, get, html_to_text, now, read_sitemaps, robots, seeds

report = []
for s in seeds():
    base = s["url"].rstrip("/") + "/"
    rp, st, text = robots(base)
    rec = {"id": s["id"], "name": s["name"], "url": base, "checked_at": now(), "robots_status": st,
           "our_agent_allowed": bool(rp and rp.can_fetch(UA, base)),
           "ai_bots_blocked": [a for a in AI_AGENTS if rp and not rp.can_fetch(a, base)],
           "allowed_paths": {p: bool(rp and rp.can_fetch(UA, base.rstrip("/") + p)) for p in s["read"]},
           "terms_url": None, "terms_flagged": []}
    if rp:
        urls, _ = read_sitemaps(base, rp)
        terms = sorted((u for u, _ in urls if TERMS_RE.search(u)), key=len)
        if terms and rp.can_fetch(UA, terms[0]):
            st2, body, final = get(terms[0])
            if st2 == 200:
                _, t = html_to_text(body)
                rec["terms_url"] = final
                rec["terms_flagged"] = [x.strip() for x in re.split(r"(?<=[.;])\s+|\n", t) if CLAUSE_RE.search(x) and 20 < len(x) < 500][:15]
    report.append(rec)
    print("%-24s robots=%s allowed=%s ai_blocked=%d terms=%s flagged=%d" % (s["id"], st, rec["our_agent_allowed"], len(rec["ai_bots_blocked"]), rec["terms_url"], len(rec["terms_flagged"])))

OUT.mkdir(exist_ok=True)
(OUT / "sources.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
md = ["# Source checks", "", "Run %s with agent `%s`. A person must read each site's terms before anything is published." % (now(), UA), ""]
for r in report:
    md += ["## " + r["name"], "",
           "- robots.txt: HTTP %s; our agent allowed: **%s**" % (r["robots_status"], "yes" if r["our_agent_allowed"] else "no"),
           "- Paths we read: " + ", ".join("`%s` %s" % (p, "allowed" if ok else "DISALLOWED") for p, ok in r["allowed_paths"].items()),
           "- AI crawlers this site blocks: " + (", ".join(r["ai_bots_blocked"]) or "none listed"),
           "- Terms page: " + (r["terms_url"] or "not found in sitemap"), ""]
    if r["terms_flagged"]:
        md += ["Sentences in the terms to read (matched words like reproduce, automated, extract):", ""] + ["> " + x for x in r["terms_flagged"]] + [""]
(OUT / "sources.md").write_text("\n".join(md))
