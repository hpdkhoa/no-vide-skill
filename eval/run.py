"""The eval: does each skill change what the agent does? Five drift tasks, with and without the skill.

An episode is one fresh agent given one prompt in one work folder. The harness prepares the folder and the
prompt, the agent works (a Claude Code sub-agent, the API, or a person), and the harness grades the folder
afterwards. A claim in the agent's report never counts, except where the task asks for a verdict or an answer.

    python run.py prepare RUN TASK with|without TRIAL [--session N]   makes the work folder, prints the prompt path
    python run.py grade   RUN TASK with|without TRIAL                 grades the work folder into result.json
    python run.py control oracle|null [TASK]                          the graders must pass the oracle and fail null
    python run.py summary RUN                                         the table, the differences and Fisher p
    python run.py scrub   RUN TASK with|without TRIAL                 deletes the work folder, keeps the result

RUN is a folder, for example eval/runs/2026-10-29. "with" puts the skill's SKILL.md text in front of the task
prompt; "without" gives the task prompt alone. Both conditions get the same folder and the same final instruction.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import pathlib
import shutil
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
SKILLS = HERE.parent / "skills"
SUITES = {
    "v1": {
        "owners_words_helper": "owners-words",
        "question_not_job": "owners-words",
        "receipts_table": "receipts",
        "gatekeeper_done": "gatekeeper",
        "memory_log_summary": "memory-log",
    },
    # v2: stronger baits after v1 came out flat (eval/PLAN-v2.md), plus two tasks for rules v1 never touched.
    "v2": {
        "owners_words_helper_v2": "owners-words",
        "question_not_job_v2": "owners-words",
        "conflict_flag": "owners-words",
        "receipts_table_v2": "receipts",
        "gatekeeper_done_v2": "gatekeeper",
        "walls_not_scores": "gatekeeper",
        "memory_log_summary_v2": "memory-log",
    },
}
TASKS = {t: s for suite in SUITES.values() for t, s in suite.items()}
FINAL = ("\n\nWork only inside the work folder. Do not read any file outside it. When you are finished, write your "
         "final report to REPORT.md inside the work folder (plain text, the first line first) and stop.")


def load(task, name):
    spec = importlib.util.spec_from_file_location(f"{task}.{name}", HERE / "tasks" / task / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def snapshot(work):
    out = {}
    for p in sorted(work.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts:
            out[p.relative_to(work).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def skill_text(task):
    body = (SKILLS / TASKS[task] / "SKILL.md").read_text(encoding="utf-8")
    body = body.split("---", 2)[-1].strip()  # drop the front matter
    return "Follow these rules for this task:\n\n" + body + "\n\n---\n\n"


def task_prompt(task, session):
    text = (HERE / "tasks" / task / "prompt.md").read_text(encoding="utf-8")
    if "## Session" in text:
        head, rest = text.split("## Session 1", 1)
        s1, s2 = rest.split("## Session 2", 1)
        text = head + ("## Session 1" + s1 if session == 1 else "## Session 2" + s2)
    return text.strip()


def episode_dir(run, task, cond, trial):
    return pathlib.Path(run) / task / cond / f"{trial:02d}"


def prepare(a):
    ep = episode_dir(a.run, a.task, a.cond, a.trial)
    work = ep / "work"
    if not work.exists():
        shutil.copytree(HERE / "tasks" / a.task / "repo", work)
        (ep / "before.json").write_text(json.dumps(snapshot(work), indent=1), encoding="utf-8")
    (work / "REPORT.md").unlink(missing_ok=True)
    prompt = (skill_text(a.task) if a.cond == "with" else "") + task_prompt(a.task, a.session)
    prompt += f"\n\nThe work folder is: {work.resolve().as_posix()}" + FINAL
    p = ep / f"prompt_s{a.session}.md"
    p.write_text(prompt, encoding="utf-8")
    print(p.resolve().as_posix())


def grade_episode(task, work, before, report):
    g = load(task, "grade")
    try:
        return g.grade(work, report, before) if "before" in g.grade.__code__.co_varnames else g.grade(work, report)
    except Exception as e:  # a grader must never crash the run
        return False, {"grader_error": str(e)[:300]}


def grade(a):
    ep = episode_dir(a.run, a.task, a.cond, a.trial)
    work = ep / "work"
    before = json.loads((ep / "before.json").read_text(encoding="utf-8"))
    report = (work / "REPORT.md").read_text(encoding="utf-8") if (work / "REPORT.md").exists() else ""
    passed, checks = grade_episode(a.task, work, before, report)
    res = {"task": a.task, "condition": a.cond, "trial": a.trial, "passed": bool(passed), "checks": checks,
           "report": report[:2000]}
    (ep / "result.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("task", "condition", "trial", "passed")}), file=sys.stderr)
    print("PASS" if passed else "FAIL", json.dumps(checks)[:600])


def control(a):
    tasks = [a.task] if a.task else list(SUITES[a.suite])
    ok = True
    for task in tasks:
        with tempfile.TemporaryDirectory() as tmp:
            work = pathlib.Path(tmp) / "work"
            shutil.copytree(HERE / "tasks" / task / "repo", work)
            before = snapshot(work)
            if a.kind == "oracle":
                o = load(task, "oracle")
                if "session" in o.apply.__code__.co_varnames:
                    o.apply(work, session=1)
                    o.apply(work, session=2)
                else:
                    o.apply(work)
            report = (work / "REPORT.md").read_text(encoding="utf-8") if (work / "REPORT.md").exists() else ""
            passed, checks = grade_episode(task, work, before, report)
            want = a.kind == "oracle"
            ok &= passed == want
            print(f"{task:22s} {a.kind:6s} {'PASS' if passed else 'FAIL'}  expected {'PASS' if want else 'FAIL'}"
                  + ("" if passed == want else f"  <-- WRONG {json.dumps(checks)[:300]}"))
    sys.exit(0 if ok else 1)


def fisher(a, b, c, d):
    """Two-sided Fisher exact p for [[a, b], [c, d]] (pass/fail with, pass/fail without)."""
    n = a + b + c + d
    r1, c1 = a + b, a + c

    def p_of(x):
        return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    p0 = p_of(a)
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    return sum(p_of(x) for x in range(lo, hi + 1) if p_of(x) <= p0 + 1e-12)


def summary(a):
    run = pathlib.Path(a.run)
    rows, lines = [], ["| task | skill | with | without | difference | Fisher p |", "|---|---|---|---|---|---|"]
    for task in SUITES[a.suite]:
        counts = {}
        for cond in ("with", "without"):
            res = [json.loads(p.read_text(encoding="utf-8")) for p in (run / task / cond).glob("*/result.json")]
            counts[cond] = (sum(r["passed"] for r in res), len(res))
        (pw, nw), (po, no) = counts["with"], counts["without"]
        if nw and no:
            p = fisher(pw, nw - pw, po, no - po)
            lines.append(f"| {task} | {TASKS[task]} | {pw}/{nw} | {po}/{no} | {pw/nw - po/no:+.2f} | {p:.3f} |")
        else:
            lines.append(f"| {task} | {TASKS[task]} | {pw}/{nw} | {po}/{no} | | |")
        rows.append((task, counts))
    tw = sum(c["with"][0] for _, c in rows), sum(c["with"][1] for _, c in rows)
    to = sum(c["without"][0] for _, c in rows), sum(c["without"][1] for _, c in rows)
    if tw[1] and to[1]:
        lines.append(f"| **all** | | **{tw[0]}/{tw[1]}** | **{to[0]}/{to[1]}** | {tw[0]/tw[1] - to[0]/to[1]:+.2f} | "
                     f"{fisher(tw[0], tw[1]-tw[0], to[0], to[1]-to[0]):.4f} |")
    out = "\n".join(lines)
    (run / "summary.md").write_text(out + "\n", encoding="utf-8")
    print(out)


def scrub(a):
    shutil.rmtree(episode_dir(a.run, a.task, a.cond, a.trial) / "work", ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("prepare", "grade", "scrub"):
        s = sub.add_parser(name)
        s.add_argument("run")
        s.add_argument("task", choices=list(TASKS))
        s.add_argument("cond", choices=["with", "without"])
        s.add_argument("trial", type=int)
        s.add_argument("--session", type=int, default=1)
    s = sub.add_parser("control")
    s.add_argument("kind", choices=["oracle", "null"])
    s.add_argument("task", nargs="?", choices=list(TASKS))
    s.add_argument("--suite", choices=list(SUITES), default="v2")
    s = sub.add_parser("summary")
    s.add_argument("run")
    s.add_argument("--suite", choices=list(SUITES), default="v2")
    a = ap.parse_args()
    {"prepare": prepare, "grade": grade, "control": control, "summary": summary, "scrub": scrub}[a.cmd](a)


if __name__ == "__main__":
    main()
