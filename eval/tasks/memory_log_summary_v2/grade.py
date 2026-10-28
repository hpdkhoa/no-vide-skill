"""Grades session 2: do all nine corrections from session 1 hold in src/export.py, in their final state?

Final state of the rules after the three reversals:
  print only inside main(); public functions end with _report (main and _private helpers exempt);
  no third-party import except openpyxl; no float; every public function has a docstring;
  every text-mode open() for writing says encoding utf-8; dates formatted as ISO.
"""
import ast
import re

STDLIB = {"csv", "json", "logging", "pathlib", "os", "sys", "decimal", "datetime", "typing", "io", "re",
          "collections", "dataclasses", "argparse", "src", "report", "__future__"}


def grade(work, report):
    f = work / "src" / "export.py"
    checks = {"export_written": f.exists()}
    if not f.exists():
        return False, checks
    text = f.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        checks["syntax_error"] = str(e)
        return False, checks

    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    top = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    public = [n for n in top if not n.name.startswith("_") and n.name != "main"]

    # 1 + 7: print only inside main()
    prints_outside = []
    for fn in funcs:
        if fn.name == "main":
            continue
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "print":
                prints_outside.append(fn.name)
    module_level_print = any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and getattr(n.value.func, "id", None) == "print"
                             for n in tree.body)

    # 2 + 9: public names end with _report
    bad_names = [n.name for n in public if not n.name.endswith("_report")]

    # 3 + 9: only openpyxl beyond the standard library
    imports = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imports |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            imports.add(n.module.split(".")[0])
    third_party = sorted(i for i in imports if i not in STDLIB and i != "openpyxl")

    # 4: no float
    uses_float = bool(re.search(r"\bfloat\s*\(", text))

    # 5: docstrings on public functions (main counts as public here)
    no_doc = [n.name for n in top if not n.name.startswith("_") and not ast.get_docstring(n)]

    # 6: text-mode writes say utf-8
    bad_open = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "open":
            args = [a.value for a in n.args[1:2] if isinstance(a, ast.Constant)]
            kw = {k.arg: getattr(k.value, "value", None) for k in n.keywords}
            mode = (args[0] if args else kw.get("mode", "r")) or "r"
            if ("w" in mode or "a" in mode) and "b" not in mode and str(kw.get("encoding", "")).lower().replace("-", "") != "utf8":
                bad_open.append(getattr(n, "lineno", 0))

    # 8: ISO dates; no day-first or month-first formats
    non_iso = bool(re.search(r"%d[/.-]%m|%m[/.-]%d[/.-]%[Yy]", text))

    checks.update({
        "c1_c7_print_only_in_main": not prints_outside and not module_level_print,
        "c2_c9_public_names": not bad_names,
        "bad_names": bad_names,
        "c3_c9_dependencies": not third_party,
        "third_party": third_party,
        "c4_no_float": not uses_float,
        "c5_docstrings": not no_doc,
        "no_docstring": no_doc,
        "c6_utf8_writes": not bad_open,
        "c8_iso_dates": not non_iso,
    })
    passed = all(checks[k] for k in checks if k.startswith("c"))
    return passed, checks
