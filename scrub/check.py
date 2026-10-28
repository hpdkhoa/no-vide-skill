"""The scrub check: nothing private, local or game-specific goes public. Exit 0 only when clean.

    python scrub/check.py            scan the repo
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP = {".git", "runs", "__pycache__", ".pytest_cache"}

# Names, paths, private projects, game words. Each is a regex.
PATTERNS = [
    r"\bKhoa\b", r"\bLan\b", r"\bMinh\b", r"\bHoa\b", r"\bNNPA\b", r"HieuLuat", r"Beastwarden", r"500kv", r"\bToangTown\b",
    r"[A-Z]:[/\\]", r"/srv/", r"84765",
    r"\bM1911\b", r"\bAR-?15\b", r"\bM24\b", r"\bM16A2\b", r"\bM107\b", r"trigger ring", r"web point", r"\bline B\b",
    r"magazine well", r"\bbolt catch\b", r"\bhandguard\b",
    r"firebase", r"claude\.ai/artifact",
]


def main():
    hits = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or SKIP & set(p.parts) or p.suffix in (".png", ".jpg", ".pyc"):
            continue
        if p.resolve() == pathlib.Path(__file__).resolve():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for pat in PATTERNS:
            for m in re.finditer(pat, text):
                line = text.count("\n", 0, m.start()) + 1
                hits.append(f"{p.relative_to(ROOT).as_posix()}:{line}  {pat}  ...{text[max(0, m.start()-20):m.end()+20]!r}")
    for h in hits:
        print(h)
    print(f"scrub: {len(hits)} hits")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
