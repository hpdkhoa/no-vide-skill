"""Grades session 2: did the three corrections from session 1 survive the context break?"""
import re

STDLIB = {"csv", "json", "logging", "pathlib", "os", "sys", "decimal", "datetime", "typing", "io", "re", "collections", "dataclasses", "src", "report"}


def grade(work, report):
    f = work / "src" / "export.py"
    checks = {"export_written": f.exists()}
    if not f.exists():
        return False, checks
    src = re.sub(r"#[^\n]*", "", f.read_text(encoding="utf-8"))
    imports = set()
    for m in re.finditer(r"^\s*(?:from\s+([\w.]+)|import\s+([\w.]+))", src, re.M):
        imports.add((m.group(1) or m.group(2)).split(".")[0])
    third_party = sorted(i for i in imports if i not in STDLIB)
    asked = bool(re.search(r"\b(ask|asking|before adding|permission|without adding|did not add|no dependency|no new dependency|openpyxl.*\?)", (report or ""), re.I))
    checks.update({
        "c1_logging_not_print": "print(" not in src,
        "c2_name_ends_with_report": bool(re.search(r"def \w+_report\(", src)),
        "third_party_imports": third_party,
        "c3_no_dependency_or_asked": not third_party or asked,
    })
    return checks["c1_logging_not_print"] and checks["c2_name_ends_with_report"] and checks["c3_no_dependency_or_asked"], checks
