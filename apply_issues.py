#!/usr/bin/env python3
"""Apply done:/note: GitHub issues (authored by Pgil26 only) to data.json."""
import json, subprocess, datetime, shutil, os, re
from zoneinfo import ZoneInfo
REPO = "Pgil26/meeting-todos"
SRC = "/home/box/agent-data/agents/f32cc9d9-7c0d-42a4-adb6-65ebf207fb81/followups-dashboard/data.json"
COPY = "/workspace/followups-dashboard/data.json"
BK = "/workspace/meeting-todos/backups"
now = datetime.datetime.now(ZoneInfo("America/New_York")); today = now.date().isoformat()
def gh(*a): return subprocess.run(["gh", *a], check=True, capture_output=True, text=True).stdout
issues = json.loads(gh("issue", "list", "-R", REPO, "--state", "open", "--limit", "200",
                       "--json", "number,title,body,author,createdAt"))
data = json.load(open(SRC)); byid = {i.get("id"): i for i in data["items"]}
applied, ignored, unknown, closes = [], [], [], []
def extract(body, label):
    m = re.search(rf"{label}:\s*(.*)", body or "", re.S | re.I)
    return m.group(1).strip() if m else ""
def addnote(item, text):
    item["note"] = (item.get("note", "").rstrip() + " | " if item.get("note") else "") + f"[{today}] {text}"
for iss in sorted(issues, key=lambda x: x["number"]):
    login = (iss.get("author") or {}).get("login"); t = iss["title"].strip()
    m = re.match(r"^(done|note):\s*(\S+)\s*$", t, re.I)
    if login != "Pgil26" or not m:
        ignored.append((iss["number"], login, t)); continue
    kind, iid = m.group(1).lower(), m.group(2)
    if iid not in byid:
        gh("issue", "comment", str(iss["number"]), "-R", REPO, "-b", f"Item id `{iid}` was not found in the tracker; leaving this open.")
        unknown.append((iss["number"], iid)); continue
    item = byid[iid]
    if kind == "done":
        text = extract(iss["body"], "Optional note")
        item["status"] = "done"; item["cleared_on"] = today
    else:
        text = extract(iss["body"], "Note")
    if text: addnote(item, text)
    if kind == "note" and not text:
        ignored.append((iss["number"], login, t + " (empty note)")); continue
    applied.append((iss["number"], iid, kind, text)); closes.append(iss["number"])
if applied:
    os.makedirs(BK, exist_ok=True)
    shutil.copy2(SRC, f"{BK}/data.json.{now.strftime('%Y%m%d-%H%M%S')}")
    data["updated_at"] = now.isoformat(timespec="seconds")
    tmp = SRC + ".tmp"; json.dump(data, open(tmp, "w"), indent=2, ensure_ascii=False); os.replace(tmp, SRC)
    os.makedirs(os.path.dirname(COPY), exist_ok=True); shutil.copy2(SRC, COPY)
    for n in closes:
        gh("issue", "comment", str(n), "-R", REPO, "-b", f"Applied to tracker on {today}")
        gh("issue", "close", str(n), "-R", REPO)
print(f"Applied {len(applied)} issue(s):")
for n, iid, k, txt in applied: print(f"  #{n} {k} {iid}" + (f" — note: {txt}" if txt else ""))
for n, iid in unknown: print(f"  #{n} UNKNOWN id {iid} (commented, left open)")
for n, l, t in ignored: print(f"  #{n} IGNORED (author {l}): {t} — left open")
