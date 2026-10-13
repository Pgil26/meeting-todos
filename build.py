#!/usr/bin/env python3
"""Build public index.html from followups data.json (open + watching only)."""
import json, re, html, datetime, urllib.parse
from zoneinfo import ZoneInfo
SRC = "/home/box/agent-data/agents/f32cc9d9-7c0d-42a4-adb6-65ebf207fb81/followups-dashboard/data.json"
OUT = "/workspace/meeting-todos/index.html"
NAMES = {}  # full names allowed per Patrick (Oct 13, 2026)
def anon(s):
    if not s: return s
    s = str(s)
    for n in sorted(NAMES, key=len, reverse=True):
        s = re.sub(r"\b%s\b" % re.escape(n), NAMES[n], s)
    s = re.sub(r"\S+@\S+\.\w+", "[email]", s)
    s = re.sub(r"\+?\d[\d\-\s().]{7,}\d", "[phone]", s)
    s = re.sub(r"\$\s?[\d,.]+\s?[KkMm]?\b", "", s)
    s = re.sub(r"\bpasswords?\b", "access", s, flags=re.I)
    return re.sub(r"\s{2,}", " ", s).replace(" —  ", " — ").strip()
now = datetime.datetime.now(ZoneInfo("America/New_York"))
today = now.date()
items = json.load(open(SRC))["items"]
ISSUE = "https://github.com/Pgil26/meeting-todos/issues/new"
def ilink(kind, i):
    t = anon(i["title"])
    body = f"Item: {t}\n\nOptional note:" if kind=="done" else f"Item: {t}\n\nNote: "
    return ISSUE + "?" + urllib.parse.urlencode({"title": f"{kind}: {i['id']}", "body": body}, quote_via=urllib.parse.quote)
def btns(i):
    return (f'<div class="btns"><a class="btn done" target="_blank" rel="noopener" href="{html.escape(ilink("done",i))}">✓ Mark done</a>'
            f'<a class="btn notebtn" target="_blank" rel="noopener" href="{html.escape(ilink("note",i))}">✎ Add note</a></div>')
def card(i):
    dl = i.get("deadline"); over = False
    if dl:
        try: over = datetime.date.fromisoformat(dl) < today
        except ValueError: pass
    due = anon(dl) if dl else "No date"
    note = f'<p class="note">{html.escape(anon(i.get("note","")))}</p>' if i.get("note") else ""
    return (f'<div class="card{" overdue" if over else ""}"><h2>{html.escape(anon(i["title"]))}</h2>'
            f'<p class="due">Due: {html.escape(due)}{" — OVERDUE" if over else ""}</p>'
            f'<p class="src">From: {html.escape(anon(i.get("meeting","")))} ({html.escape(i.get("meeting_date") or "")})</p>{note}{btns(i)}</div>')
op = [i for i in items if i.get("status")=="open"]
wa = [i for i in items if i.get("status")=="watching"]
doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Patrick's open meeting to-dos</title><style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;font-size:19px;line-height:1.5;margin:0;padding:16px;background:#f4f5f7;color:#1a1a1a}}
main{{max-width:760px;margin:auto}}h1{{font-size:1.7em;margin:.2em 0}}.upd{{color:#666}}
h3{{margin-top:1.6em;font-size:1.3em}}.card{{background:#fff;border-radius:12px;padding:16px 18px;margin:14px 0;box-shadow:0 1px 3px #0002;border-left:6px solid #3b82f6}}
.card h2{{font-size:1.15em;margin:0 0 .4em}}.card p{{margin:.25em 0}}.src,.note{{color:#555;font-size:.9em}}
.overdue{{border-left-color:#dc2626}}.overdue .due{{color:#dc2626;font-weight:700}}.watch .card{{border-left-color:#9ca3af;opacity:.9}}
.btns{{display:flex;gap:10px;margin-top:12px;flex-wrap:wrap}}.btn{{flex:1 1 140px;text-align:center;padding:14px 10px;min-height:48px;box-sizing:border-box;border-radius:10px;font-weight:700;font-size:1em;text-decoration:none;color:#fff}}
.btn.done{{background:#16a34a}}.btn.notebtn{{background:#2563eb}}.help{{color:#444;font-size:.9em;margin:.3em 0}}
</style></head><body><main><h1>Patrick's open meeting to-dos</h1><div class="upd">Updated {now.strftime('%b %-d, %Y %-I:%M %p')} ET</div>
<p class="help">Tap Done or Note, then press Submit on GitHub. The tracker updates the next weekday morning.</p>
<h3>Open ({len(op)})</h3>{''.join(map(card,op)) or '<p>Nothing open.</p>'}
<div class="watch"><h3>Watching ({len(wa)})</h3>{''.join(map(card,wa)) or '<p>None.</p>'}</div></main></body></html>"""
open(OUT,"w").write(doc)
print(f"wrote {OUT}: {len(op)} open, {len(wa)} watching")
