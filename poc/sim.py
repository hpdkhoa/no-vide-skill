"""Fast compaction test: a long session is squeezed into a summary, then a fresh agent must keep the owner's rules.

    python sim.py hooks            run the session through the real hook commands; print ledger, recall block, sizes
    python sim.py prepare K        write K summarizer prompts and their continuation prompts (with / without recall)
    python sim.py probe K          after the summaries exist, write the continuation prompts for trial K
    python sim.py grade            grade every answer file

Not a full eval: one scenario, a few trials, a simulated compaction (an agent writes the summary under a word cap).
"""
import json
import pathlib
import random
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE / "run"
NV = [sys.executable, str(HERE / "nv.py")]

# (owner message, what the agent does after it: None, or ["done", start of the ask it closes])
SESSION = [
    ("build a script that reads sales.csv and writes a monthly excel report, use openpyxl for the excel part", None),
    ("money must always be Decimal, never float", None),
    ("what is the difference between xlsxwriter and openpyxl?", None),
    ("ok", None),
    ("use the _report suffix for public function names so I can find them", None),
    ("add a totals row at the bottom", None),
    ("show me the output for march", ["done", "show me the output"]),
    ("the totals row looks good", ["done", "add a totals row"]),
    ("keep print only inside main, the helpers return values", None),
    ("why the date shows 28/10/2026? use ISO dates", None),
    ("now write the region breakdown sheet", None),
    ("switch to xlsxwriter, not openpyxl, it is faster for big files", None),
    ("nice, that is fast", None),
    ("once again the date is day first in the region sheet, dates are ISO everywhere", ["done", "now write the region"]),
    ("don't add a chart yet", None),
    ("drop the _report suffix, names should be short", None),
    ("can you explain how the region totals are computed?", ["done", "can you explain"]),
    ("write a short README section on usage", None),
    ("every file write must say encoding utf-8", None),
    ("how long will the full year take to run?", None),
    ("run it on the 2025 file and show me the timing", None),
    ("good, 3 seconds is fine", ["done", "run it on the 2025"]),
    ("keep the chart out until I say", None),
    ("continue", None),
]

# The rules that must survive, as multiple-choice probes. key = the right letter.
PROBES = [
    ("Which library writes the Excel file?", ["openpyxl", "xlsxwriter"], "xlsxwriter"),
    ("Which type holds money amounts?", ["float", "Decimal"], "Decimal"),
    ("Public name for the function that builds the totals sheet?", ["totals_report", "totals"], "totals"),
    ("How is a date written in a cell?", ["28/10/2026", "2026-10-28"], "2026-10-28"),
    ("May a helper function print a debug line?", ["yes", "no, print only in main"], "no, print only in main"),
    ("Add a chart to the region sheet now?", ["yes", "no, not until the owner says"], "no, not until the owner says"),
    ("How to open a text file for writing?", ['open(p, "w")', 'open(p, "w", encoding="utf-8")'], 'open(p, "w", encoding="utf-8")'),
    ("Which owner ask is still open?", ["the totals row", "a README section on usage", "the 2025 timing"], "a README section on usage"),
]


def assistant_turn(i, msg):
    """A long, noisy assistant turn, like a real session with tool output."""
    rnd = random.Random(i)
    lines = [f"Working on: {msg[:60]}", "Ran: python export.py --month 03"]
    for k in range(40):
        lines.append(f"  row {rnd.randint(1, 9000):5d} region={rnd.choice(['north', 'south', 'east', 'west'])} "
                     f"amount={rnd.randint(10, 99999)}.{rnd.randint(0, 99):02d} ok")
    lines.append("diff --git a/export.py b/export.py")
    lines += [f"+    line {k}: cell = ws.cell(row=r, column={k % 9 + 1})" for k in range(12)]
    lines.append("Done. Tests: 14 passed.")
    return "\n".join(lines)


def transcript():
    out = []
    for i, (msg, _) in enumerate(SESSION):
        out.append(f"USER: {msg}")
        out.append(f"ASSISTANT: {assistant_turn(i, msg)}")
    return "\n\n".join(out)


def hook(cmd, event):
    return subprocess.run(NV + [cmd], input=json.dumps(event), capture_output=True, text=True,
                          encoding="utf-8").stdout


def run_hooks():
    work = RUN / "project"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    ev = {"cwd": str(work)}
    for msg, act in SESSION:
        hook("capture", dict(ev, prompt=msg))
        if act:
            led = (work / ".novibes" / "ledger.txt").read_text(encoding="utf-8").splitlines()
            lid = next(x.split()[0] for x in led if x.split(" ", 4)[4].startswith(act[1]))
            subprocess.run(NV + [act[0], lid], cwd=work, capture_output=True)
        hook("stop", dict(ev, reply="(the agent answers)"))  # Stop hook: a question just asked is answered
    todo = {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "TodoWrite", "input": {"todos": [
        {"content": "monthly sheet", "status": "completed"}, {"content": "region sheet", "status": "completed"},
        {"content": "README usage section", "status": "in_progress"}, {"content": "full year run", "status": "pending"}]}}]}}
    (work / "transcript.jsonl").write_text(json.dumps(todo) + "\n", encoding="utf-8")
    hook("precompact", dict(ev, transcript_path=str(work / "transcript.jsonl"), trigger="auto"))
    recall = hook("restore", dict(ev, source="compact"))
    (RUN / "recall.txt").write_text(recall, encoding="utf-8")
    ledger = (work / ".novibes" / "ledger.txt").read_text(encoding="utf-8")
    owner = "\n".join(m for m, _ in SESSION)
    full = transcript()
    (RUN / "transcript.txt").write_text(full, encoding="utf-8")
    tok = lambda t: len(t) // 4
    print(ledger)
    print("---- recall block ----")
    print(recall)
    print(f"tokens: transcript {tok(full)}, owner messages {tok(owner)}, ledger {tok(ledger)}, recall {tok(recall)}")


def summarizer_prompt(cap):
    return ("You are the context compactor of a coding assistant. The conversation below is too long for the context "
            "window. Write the summary that will replace it, so the assistant can continue the work. Keep what the "
            f"assistant needs. Hard limit: {cap} words. Reply with the summary only.\n\n" + transcript())


def probe_text(seed):
    rnd = random.Random(seed)
    lines, key = [], {}
    for n, (q, opts, right) in enumerate(PROBES, 1):
        opts = opts + ["not stated"]
        rnd.shuffle(opts)
        letters = "abcd"
        lines.append(f"Q{n}. {q} " + "  ".join(f"{letters[i]}) {o}" for i, o in enumerate(opts)))
        key[f"Q{n}"] = letters[opts.index(right)]
    return "\n".join(lines), key


def prepare(k, cap=250, first=1):
    RUN.mkdir(exist_ok=True)
    for t in range(first, first + k):
        (RUN / f"t{t}").mkdir(exist_ok=True)
        (RUN / f"t{t}" / "summarize_prompt.md").write_text(
            summarizer_prompt(cap), encoding="utf-8")
        print((RUN / f"t{t}" / "summarize_prompt.md").as_posix())


def probe(t):
    d = RUN / f"t{t}"
    summary = (d / "summary.md").read_text(encoding="utf-8")
    recall = (RUN / "recall.txt").read_text(encoding="utf-8")
    text, key = probe_text(t)
    (d / "key.json").write_text(json.dumps(key), encoding="utf-8")
    for cond in ("with", "without"):
        body = ("This session was compacted. Summary of the earlier conversation:\n\n" + summary + "\n\n"
                + (recall + "\n\n" if cond == "with" else "")
                + "The owner now says: \"continue\".\n\nBefore you write any code, answer these from what you know of "
                  "the owner's rules and decisions. Pick one letter each. Do not read any files.\n\n" + text
                + "\n\nReply with only JSON like {\"Q1\": \"a\", ...} and stop.")
        (d / f"probe_{cond}.md").write_text(body, encoding="utf-8")
        print((d / f"probe_{cond}.md").as_posix())


def grade():
    rows = {"with": [], "without": []}
    for d in sorted(RUN.glob("t[0-9]*")):
        key = json.loads((d / "key.json").read_text(encoding="utf-8"))
        for cond in rows:
            f = d / f"answer_{cond}.json"
            if not f.exists():
                continue
            ans = json.loads(f.read_text(encoding="utf-8"))
            right = [q for q in key if str(ans.get(q, "")).strip().lower()[:1] == key[q]]
            rows[cond].append(len(right))
            missed = [PROBES[int(q[1:]) - 1][0] for q in key if q not in right]
            print(f"{d.name} {cond:7s} {len(right)}/{len(key)}  missed: {missed}")
    for cond, s in rows.items():
        if s:
            print(f"{cond}: {sum(s)}/{len(s) * len(PROBES)} over {len(s)} trials")


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"hooks": lambda: run_hooks(), "prepare": lambda: prepare(*map(int, sys.argv[2:])),
     "probe": lambda: probe(int(sys.argv[2])), "grade": lambda: grade()}[cmd]()
