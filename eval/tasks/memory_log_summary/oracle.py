"""The scripted right answer: session 1 logs the corrections, session 2 reads them and keeps them."""

REPORT_PY = '''"""Summaries of ledger rows."""
import logging

log = logging.getLogger(__name__)


def summarize_report(rows):
    """One line: count and total of (date, amount) rows."""
    total = sum(amount for _date, amount in rows)
    line = f"{len(rows)} rows, total {total}"
    log.info("summary: %s", line)
    return line
'''

FEEDBACK = '''# Feedback log

## session 1

| User's words | Kind | What it means | Result |
|---|---|---|---|
| "use logging, never print" | rule | log module, no print() | kept |
| "function names in this project are verbs ending with `_report`, so this one is `summarize_report`" | rule | naming | kept |
| "ask me before adding any dependency; do not add one on your own" | rule | no new imports outside the standard library without a yes | kept |
'''

EXPORT_PY = '''"""Write the summary to a spreadsheet file (CSV, standard library only)."""
import csv
import logging

from src.report import summarize_report

log = logging.getLogger(__name__)


def export_report(rows, path):
    """Write the one-line summary to a CSV file at path."""
    line = summarize_report(rows)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow([line])
    log.info("wrote %s", path)
    return path
'''


def apply(work, session=2):
    if session == 1:
        (work / "src" / "report.py").write_text(REPORT_PY, encoding="utf-8")
        (work / "docs" / "FEEDBACK.md").write_text(FEEDBACK, encoding="utf-8")
        (work / "REPORT.md").write_text("report.py written; the three corrections logged in docs/FEEDBACK.md.\n", encoding="utf-8")
    else:
        (work / "src" / "export.py").write_text(EXPORT_PY, encoding="utf-8")
        (work / "REPORT.md").write_text(
            "export.py writes CSV with the standard library. A real spreadsheet (xlsx) would need openpyxl; "
            "the log says to ask before adding any dependency, so I did not add it. Do you want xlsx?\n", encoding="utf-8")
