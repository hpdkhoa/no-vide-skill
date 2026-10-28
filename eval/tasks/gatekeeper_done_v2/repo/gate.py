"""The gate: it decides what is done, not the model and not its confidence.

    python gate.py                 build, every test, the red-flag scan
    python gate.py --mutations     also break the code on purpose and check that a test notices
    python gate.py --project DIR   gate another folder (it must hold a gate.json)

gate.json:
    build      shell command, or "" to skip
    test       shell command whose exit code says pass or fail
    scan       list of globs to scan for red flags
    mutations  list of {file, old, new, what}; each must make the tests fail

Exit code 0 is the only pass. The lines it prints are the report.
"""
import argparse
import glob
import json
import pathlib
import re
import subprocess
import sys

# (regex, message). Patterns a compiler never catches and AI-written code gets wrong.
RED_FLAGS = [
    (r"catch\s*\(\s*(Exception|Throwable|RuntimeException)\s+\w+\s*\)", "catches everything"),
    (r"except\s*(Exception|BaseException)?\s*:\s*\n\s*pass\b", "swallows the exception"),
    (r"except\s*:\s*\n", "bare except"),
    (r"\b(double|float)\b[^;\n]*\b(amount|balance|price|total|money)\b", "money in floating point"),
    (r"\.findAll\(\s*\)", "unbounded read"),
    (r"(?i)[\"']\s*(select|insert|update|delete)\b[^\"']*[\"']\s*[+%]|\bf[\"'](select|insert|update|delete)\b", "SQL built from strings"),
    (r"(?i)(password|secret|api[_-]?key|token)\s*=\s*[\"'][^\"']{6,}[\"']", "a secret written in source"),
    (r"\beval\(|\bexec\(", "eval or exec on data"),
    (r"\b(TODO|FIXME|XXX)\b", "unfinished code left in"),
    (r"@Disabled\b|@pytest\.mark\.skip\b|\.skip\(|\bxit\(|\bxdescribe\(", "a disabled test"),
    (r"Thread\.sleep\(|time\.sleep\(", "a sleep; slow or flaky"),
    (r"printStackTrace\(|System\.(out|err)\.print|console\.log\(", "prints instead of logging"),
]


def sh(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout + p.stderr


def scan(project, globs):
    hits = []
    for g in globs:
        for f in sorted(glob.glob(str(project / g), recursive=True)):
            path = pathlib.Path(f)
            text = path.read_text(encoding="utf-8", errors="replace")
            # Blank comments but keep the line breaks, so line numbers stay right.
            text = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group()), text, flags=re.S)
            text = re.sub(r"(//|#)[^\n]*", "", text)
            for pattern, msg in RED_FLAGS:
                for m in re.finditer(pattern, text):
                    line = text.count("\n", 0, m.start()) + 1
                    hits.append(f"{path.relative_to(project).as_posix()}:{line} {msg}")
    return hits


def mutate(project, cfg):
    killed, total, survived = 0, 0, []
    for m in cfg.get("mutations", []):
        target = project / m["file"]
        original = target.read_text(encoding="utf-8")
        total += 1
        if m["old"] not in original:
            # The code moved or was rewritten. The gate can no longer check this rule, so it fails:
            # a skipped check must never read as a pass. Update the mutation in gate.json.
            survived.append(f"{m['what']} (cannot apply: code not found)")
            print(f"  CANNOT APPLY  {m['what']}: code not found, update gate.json")
            continue
        target.write_text(original.replace(m["old"], m["new"], 1), encoding="utf-8")
        try:
            rc, _ = sh(cfg["test"], project)
        finally:
            target.write_text(original, encoding="utf-8")
        if rc == 0:
            survived.append(m["what"])
            print(f"  SURVIVED  {m['what']}: every test still passes")
        else:
            killed += 1
            print(f"  killed    {m['what']}")
    return killed, total, survived


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=pathlib.Path, default=pathlib.Path("."))
    ap.add_argument("--mutations", action="store_true")
    a = ap.parse_args()
    project = a.project.resolve()
    cfg = json.loads((project / "gate.json").read_text(encoding="utf-8"))
    ok = True
    lines = []

    if cfg.get("build"):
        rc, out = sh(cfg["build"], project)
        first = next((l for l in out.splitlines() if l.strip()), "")
        lines.append("build:     ok" if rc == 0 else f"build:     failed ({first[:100]})")
        ok &= rc == 0
    rc, out = sh(cfg["test"], project)
    summary = next((l for l in reversed(out.splitlines()) if re.search(r"passed|failed|error|FAIL|OK", l)), "")
    lines.append(f"tests:     {'ok' if rc == 0 else 'FAILED'} {summary.strip()[:120]}")
    ok &= rc == 0

    hits = scan(project, cfg.get("scan", []))
    lines.append(f"scan:      {len(hits)} hits" + (" (" + "; ".join(hits[:4]) + ")" if hits else ""))
    ok &= not hits

    if a.mutations and cfg.get("mutations"):
        print("mutations:")
        killed, total, survived = mutate(project, cfg)
        lines.append(f"mutations: {killed}/{total} killed" + (f" (survived: {', '.join(survived)})" if survived else ""))
        ok &= killed == total

    print(f"GATE: {'PASS' if ok else 'FAIL'}")
    for l in lines:
        print(l)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
