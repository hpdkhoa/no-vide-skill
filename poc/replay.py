"""Replay real Claude Code transcripts through the ledger and check each real compaction summary.

    python replay.py OUT_DIR TRANSCRIPT.jsonl [...]

For every compaction: the ledger as it stood (all owner clauses so far, open ones only), and for each clause the share
of its content words found in the summary. Writes OUT_DIR/rows.tsv and prints totals. No model calls.
"""
import json
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nv  # noqa: E402


def text_of(d):
    c = d["message"]["content"]
    if isinstance(c, str):
        return c
    return "\n".join(p.get("text", "") for p in c if p.get("type") == "text")


def owner_prompt(d):
    """A message the owner typed: not meta, not a tool result, not a command echo or a notification."""
    if d.get("type") != "user" or d.get("isMeta") or d.get("isSidechain") or d.get("isCompactSummary"):
        return None
    c = d["message"]["content"]
    if isinstance(c, list) and any(p.get("type") == "tool_result" for p in c):
        return None
    t = text_of(d).strip()
    if not t or t.startswith("<") or t.startswith("[Request interrupted") or t.startswith("This session is being continued"):
        return None
    return t


def kept(words, summary_words):
    w = nv.words_of(words.replace(" ...", ""))
    return len(w & summary_words) / len(w) if w else 1.0


def main():
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    rows = ["session\tcompaction\tid\tclass\tkept\tin_recall\tsummary_tokens\tledger_tokens\trecall_tokens\twords"]
    for f in sys.argv[2:]:
        name = pathlib.Path(f).stem[:8]
        work = out / name
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir()
        k, reply = 0, []
        for line in open(f, encoding="utf-8"):
            if '"type":"user"' not in line and '"type":"assistant"' not in line:
                continue
            try:
                d = json.loads(line, strict=False)
            except ValueError:
                continue  # a cut-off line
            if d.get("type") == "assistant":
                if not d.get("isSidechain") and isinstance(d["message"].get("content"), list):
                    reply += [c.get("text", "") for c in d["message"]["content"] if c.get("type") == "text"]
                continue
            p = owner_prompt(d)
            if p or d.get("isCompactSummary"):
                if reply:
                    shut = nv.stop({"cwd": str(work), "reply": "\n".join(reply)})  # the Stop hook at the end of the turn
                    if shut:
                        by = {r["id"]: r["words"] for r in nv.read_ledger(work / ".novibes")}
                        tail = " ".join(reply)[-300:].replace("\n", " ")
                        with open(out / "closes.tsv", "a", encoding="utf-8") as cl:
                            for i in shut.split()[2:]:
                                cl.write(f"{name}\t{i}\t{by[i][:120]}\t{tail}\n")
                reply = []
            if p:
                nv.capture({"cwd": str(work), "prompt": p})
            elif d.get("isCompactSummary"):
                k += 1
                summary = text_of(d)
                sw = nv.words_of(summary)
                led = nv.read_ledger(work / ".novibes")
                ledger_text = (work / ".novibes" / "ledger.txt").read_text(encoding="utf-8") if led else ""
                recall = nv.restore({"cwd": str(work), "source": "compact"}) or ""
                for r in led:
                    if r["st"] == "o":
                        rows.append(f"{name}\t{k}\t{r['id']}\t{r['cls']}\t{kept(r['words'], sw):.2f}\t{int(' ' + r['id'] + ' ' in recall)}\t"
                                    f"{nv.tokens(summary)}\t{nv.tokens(ledger_text)}\t{nv.tokens(recall)}\t{r['words']}")
        print(name, "compactions", k, flush=True)
    (out / "rows.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
