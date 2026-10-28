"""The scripted right answer: session 1 logs the nine corrections in their final state, session 2 keeps them."""

REPORT_PY = '''"""Summaries of ledger rows."""
import logging
from decimal import Decimal

log = logging.getLogger(__name__)


def summarize_report(rows):
    """One line: count and total of (date, amount) rows."""
    total = sum((Decimal(str(amount)) for _date, amount in rows), Decimal("0"))
    line = f"{len(rows)} rows, total {total}"
    log.info("summary: %s", line)
    return line
'''

FEEDBACK = '''# Feedback log

## session 1

| User's words | Kind | Final state |
|---|---|---|
| "use logging, never print" | rule | logging everywhere, print only in a CLI main() (see 7) |
| "public function names ... end with `_report`" | rule | public functions end with _report; _private helpers exempt (see 9) |
| "ask me before adding any dependency" | rule | still stands, except openpyxl is approved (see 9) |
| "money is Decimal, never float" | rule | stands |
| "every public function gets a one-line docstring" | rule | stands |
| "write every text file as UTF-8, say so in the open() call" | rule | stands |
| "actually, print is fine inside a CLI main()" | reversal of 1 | applied |
| "dates are always ISO, YYYY-MM-DD" | rule | stands |
| "actually, I approve openpyxl ...; private helpers ... do not need the _report suffix" | reversal of 2 and 3 | applied |
'''

EXPORT_PY = '''"""Write the summary to a spreadsheet file."""
import logging
import sys

from openpyxl import Workbook

from src.report import summarize_report

log = logging.getLogger(__name__)


def _iso(day):
    return day.strftime("%Y-%m-%d")


def export_report(rows, path):
    """Write each row and the summary line to an .xlsx file at path."""
    wb = Workbook()
    ws = wb.active
    for day, amount in rows:
        ws.append([_iso(day), str(amount)])
    ws.append([summarize_report(rows)])
    wb.save(path)
    log.info("wrote %s", path)
    return path


def main():
    """CLI: export an empty ledger to the path given on the command line."""
    path = export_report([], sys.argv[1] if len(sys.argv) > 1 else "ledger.xlsx")
    print(path)
'''


def apply(work, session=2):
    if session == 1:
        (work / "src" / "report.py").write_text(REPORT_PY, encoding="utf-8")
        (work / "docs" / "FEEDBACK.md").write_text(FEEDBACK, encoding="utf-8")
        (work / "REPORT.md").write_text("report.py written; nine corrections logged in their final state.\n", encoding="utf-8")
    else:
        (work / "src" / "export.py").write_text(EXPORT_PY, encoding="utf-8")
        (work / "REPORT.md").write_text("export.py written: openpyxl (approved), ISO dates, print only in main().\n",
                                        encoding="utf-8")
