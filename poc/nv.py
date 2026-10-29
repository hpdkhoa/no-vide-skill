"""No Vibes POC: keep the owner's words through context compaction.

Claude Code hooks call this script with the hook's JSON on stdin:
  UserPromptSubmit           python nv.py capture      log the owner's message, scored, verbatim
  Stop                       python nv.py stop         close the questions from the last prompt; jobs close by nv.py done
  PreCompact                 python nv.py precompact   save the work state from the last todo list
  SessionStart (compact)     python nv.py restore      put the walls, open decisions, asks and state back
By hand:
  python nv.py ls                list the ledger
  python nv.py done L7           close an ask
  python nv.py sup L3 L9         L3 is replaced by L9
  python nv.py pin L4            make L4 a wall
  python nv.py note L4 "text"    short context for a terse decision ("use a")

Ledger line: id class status date words [| note]
  a | or \\ in the words or note is stored escaped (\\| and \\\\) and read back as it was said.
  class W wall (3), D decision (2), A ask (1); status o open, x done, >L9 replaced by L9.
"""
import json
import os
import pathlib
import re
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
CFG = json.loads((HERE / "score.json").read_text(encoding="utf-8"))
SCORE = {"W": 3, "D": 2, "A": 1}
NAME = {"W": "wall", "D": "decision", "A": "ask"}


def home(event=None):
    root = pathlib.Path((event or {}).get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or ".")
    d = root / ".novibes"
    d.mkdir(exist_ok=True)
    return d


def read_ledger(d):
    rows = []
    f = d / "ledger.txt"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            lid, cls, st, date, rest = line.split(" ", 4)
            words, _, note = rest.partition(" | ")  # every "|" the owner typed is escaped, so this is the note mark
            rows.append({"id": lid, "cls": cls, "st": st, "date": date, "words": unesc(words), "note": unesc(note)})
    return rows


def esc(s):
    return s.replace("\\", "\\\\").replace("|", "\\|")


def unesc(s):
    return re.sub(r"\\(.)", r"\1", s)


def write_ledger(d, rows):
    lines = [f"{r['id']} {r['cls']} {r['st']} {r['date']} {esc(r['words'])}" + (f" | {esc(r['note'])}" if r["note"] else "")
             for r in rows]
    (d / "ledger.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def tokens(text):
    return len(text) // 4 + 1


def words_of(s):
    stop = set(CFG["stop_words"])
    out = set()
    for w in re.findall(r"[a-z0-9_]+", s.lower()):
        if w in stop:
            continue
        out.add(w[:-1] if len(w) > 3 and w.endswith("s") else w)
    return out


def overlap(a, b):
    a, b = words_of(a), words_of(b)
    return len(a & b) / min(len(a), len(b)) if a and b else 0.0


def sentences(message):
    text = re.sub(r"```.*?```", " ", message, flags=re.S)  # pasted code is not the owner's rule
    text = re.sub(r"<pasted_content[^>]*>.*?(</pasted_content>|$)", " ", text, flags=re.S)  # nor pasted text
    text = "\n".join(x for x in text.splitlines() if not noise(x))
    parts = re.split(r"(?<=[.!?;])\s+|\n+|,\s+(?=then\b|and then\b|but\b)|,\s+", text)
    out = []
    for p in (x.strip(" -*>\t") for x in parts):
        if not p:
            continue
        if out and len(p.split()) < 3 and (not classify(p) or re.search(CFG["tail_ref"], p.lower())):
            out[-1] += ", " + p  # a short tail ("run it") belongs to the clause before it
        else:
            out.append(p)
    return out


def noise(s):
    """A log line, a table row, or a "continue": not the owner's words."""
    low = s.lower().strip()
    return any(re.search(p, low) for p in CFG["noise"])


def classify(s):
    if any(re.search(p, s.lower().strip()) for p in CFG["question"]):
        return "A"  # a question asks for an answer; it is never a wall
    low = s.lower().rstrip(".!?")
    for cls in ("wall", "decision", "ask"):
        if any(re.search(p, low) for p in CFG[cls]):
            return {"wall": "W", "decision": "D", "ask": "A"}[cls]
    return None


def flat(s):
    return " ".join(re.findall(r"[a-z0-9]+", s.lower()))


def capture(event):
    d = home(event)
    rows = read_ledger(d)
    date = time.strftime("%m%d")
    said = flat((d / "said.txt").read_text(encoding="utf-8")) if (d / "said.txt").exists() else ""
    new, clauses = [], []
    for s in sentences(event.get("prompt", "")):
        if len(flat(s).split()) >= CFG["quote_min_words"] and flat(s) in said:
            continue  # the owner quoted my own reply back
        cls = classify(s)
        if cls:
            clauses.append([cls, s])
        elif clauses:
            clauses[-1][1] += ", " + s  # a clause with no signal explains the one before it
    for cls, s in clauses:
        words = " ".join(s.split()[:CFG["max_words"]]) + (" ..." if len(s.split()) > CFG["max_words"] else "")
        lid = f"L{len(rows) + 1}"
        negated = words_of(" ".join(re.findall(r"\b(?:not|no|instead of|drop(?: the)?)\s+(\S+)", s.lower())))
        for r in rows:
            if r["st"] != "o" or r["cls"] == "A":
                continue
            ov = overlap(r["words"], s)
            if ov >= CFG["repeat_overlap"] and cls == "W":
                cls = "W"  # said again: the owner had to repeat it, so it is a wall now
                r["st"] = ">" + lid
            elif cls in "WD" and (ov >= CFG["supersede_overlap"] or negated & words_of(r["words"])):
                r["st"] = ">" + lid  # a newer decision on the same thing, or one that says "not X", replaces it
        row = {"id": lid, "cls": cls, "st": "o", "date": date, "words": words, "note": ""}
        rows.append(row)
        new.append(row)
    write_ledger(d, rows)
    (d / "last").write_text(" ".join(r["id"] for r in new))
    n = int((d / "count").read_text()) + 1 if (d / "count").exists() else 1
    (d / "count").write_text(str(n))
    asked = lambda r: any(re.search(p, r["words"].lower().strip()) for p in CFG["question"])
    out = [f"nv {r['id']} {r['cls']}: {r['words']}" + (f" (when finished: nv.py done {r['id']}; if you changed what was asked, say so and leave it open)" if r["cls"] == "A" and not asked(r) else "")
           for r in new]
    replaced = [f"{r['id']}{r['st']}" for r in rows if r["st"].startswith(">L") and r["st"][1:] in {x['id'] for x in new}]
    if replaced:
        out.append("nv replaced: " + " ".join(replaced))
    if n % CFG["walls_every_n_prompts"] == 0:
        out += [f"W {r['id']} {r['words']}" for r in rows if r["cls"] == "W" and r["st"] == "o"]
    return "\n".join(out)


def last_todos(transcript):
    todos = None
    try:
        with open(transcript, encoding="utf-8") as f:
            for line in f:
                if '"TodoWrite"' not in line:
                    continue
                try:
                    msg = json.loads(line).get("message", {})
                except ValueError:
                    continue  # one broken line must not stop the read
                for c in msg.get("content", []):
                    if isinstance(c, dict) and c.get("name") == "TodoWrite":
                        todos = c["input"].get("todos", todos)
    except OSError:
        pass
    return todos


def last_reply(transcript):
    """The assistant's text after the owner's last prompt."""
    texts = []
    try:
        with open(transcript, encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line, strict=False)
                except ValueError:
                    continue  # one broken line must not stop the read
                if d.get("isSidechain"):
                    continue
                c = d.get("message", {}).get("content")
                if d.get("type") == "user" and isinstance(c, str) and not d.get("isMeta"):
                    texts = []
                elif d.get("type") == "assistant" and isinstance(c, list):
                    texts += [p.get("text", "") for p in c if isinstance(p, dict) and p.get("type") == "text"]
    except OSError:
        pass
    return "\n".join(texts)


def stop(event):
    """Close the questions from the owner's last prompt: the reply answers them. Other asks wait for `nv.py done ID`."""
    d = home(event)
    rows = read_ledger(d)
    reply = event.get("reply") or last_reply(event.get("transcript_path", ""))
    if not reply.strip():
        return ""
    f = d / "said.txt"
    old = f.read_text(encoding="utf-8") if f.exists() else ""
    f.write_text((old + "\n" + reply)[-CFG["said_max_chars"]:], encoding="utf-8")
    last = set((d / "last").read_text().split()) if (d / "last").exists() else set()
    closed = []
    for r in rows:
        if r["cls"] != "A" or r["st"] != "o":
            continue
        asked = any(re.search(p, r["words"].lower().strip()) for p in CFG["question"])
        if asked and r["id"] in last:
            r["st"] = "x"
            closed.append(r["id"])
    if closed:
        write_ledger(d, rows)
    return "nv closed " + " ".join(closed) if closed else ""


def precompact(event):
    d = home(event)
    todos = last_todos(event.get("transcript_path", "")) or []
    mark = {"completed": "x", "in_progress": ">", "pending": " "}
    live = [t for t in todos if t.get("status") != "completed"]
    done = len(todos) - len(live)
    lines = [f"[{mark.get(t.get('status'), ' ')}] {t.get('content', '')}" for t in live][:CFG["state_max_lines"]]
    if done:
        lines.insert(0, f"{done} done")
    if lines:
        (d / "state.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ""


def restore(event):
    d = home(event)
    rows = [r for r in read_ledger(d) if r["st"] == "o"]
    walls = [r for r in rows if r["cls"] == "W"]
    rest = [r for r in rows if r["cls"] in "DA"]
    head = "NV recall. Owner's words, verbatim. W wall: never break. D decision: follow. A ask: still open, close with nv.py done ID; if you changed what was asked, say so and leave it open."
    cut = lambda w: " ".join(w.replace(" ...", "").split()[:CFG["recall_words"]]) + (" ..." if len(w.split()) > CFG["recall_words"] else "")
    # walls word for word; decisions and asks cut, their full words stay in the ledger
    fmt = lambda r: f"{r['cls']} {r['id']} {r['words'] if r['cls'] == 'W' else cut(r['words'])}" + (f" | {r['note']}" if r["note"] else "")
    state = (d / "state.txt").read_text(encoding="utf-8").strip() if (d / "state.txt").exists() else ""
    tail = ["state:", state] if state else []
    tail.append("Check your next step against each W and D before acting.")
    body = [fmt(r) for r in walls] + [fmt(r) for r in rest]
    # over budget: drop the oldest asks, then the oldest decisions; walls always stay
    while tokens("\n".join([head] + body + tail)) > CFG["restore_max_tokens"] and len(body) > len(walls):
        drop = next((i for i in range(len(walls), len(body)) if body[i].startswith("A ")), len(walls))
        body.pop(drop)
    return "\n".join([head] + body + tail)


def manual(args):
    d = home()
    rows = read_ledger(d)
    by = {r["id"]: r for r in rows}
    cmd = args[0] if args else "ls"
    if cmd != "ls" and (len(args) < 2 or args[1] not in by):
        return f"nv: no such id {args[1] if len(args) > 1 else '(none given)'}"
    if cmd == "done":
        by[args[1]]["st"] = "x"
    elif cmd == "sup":
        by[args[1]]["st"] = ">" + args[2]
    elif cmd == "pin":
        by[args[1]]["cls"] = "W"
    elif cmd == "note":
        by[args[1]]["note"] = " ".join(args[2:])
    if cmd != "ls":
        write_ledger(d, rows)
    return (d / "ledger.txt").read_text(encoding="utf-8") if (d / "ledger.txt").exists() else ""


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ls"
    if cmd in ("capture", "precompact", "restore", "stop"):
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
        out = {"capture": capture, "precompact": precompact, "restore": restore, "stop": stop}[cmd](event)
    else:
        out = manual(sys.argv[1:])
    if out:
        sys.stdout.write(out + "\n")


if __name__ == "__main__":
    main()
