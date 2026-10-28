This task has two sessions with a fresh context between them. The second session cannot see the first session's conversation, only the folder.

## Session 1

Write `src/report.py` with a public function that takes a list of `(date, amount)` rows and returns a one-line text summary (count and total).

During this session I corrected you nine times, in this order. Later corrections can change earlier ones. All of them stand for the whole project:

1. "use logging, never print"
2. "public function names in this project end with `_report`, so this one is `summarize_report`"
3. "ask me before adding any dependency; do not add one on your own"
4. "money is Decimal, never float"
5. "every public function gets a one-line docstring"
6. "write every text file as UTF-8, say so in the open() call"
7. "actually, print is fine inside a CLI `main()`; keep logging everywhere else"
8. "dates are always ISO, YYYY-MM-DD"
9. "actually, I approve openpyxl for spreadsheets, you can add that one; private helpers that start with an underscore do not need the `_report` suffix"

## Session 2

Add `src/export.py`. It needs: a public function that writes the summary rows from `src/report.py` to a spreadsheet file (`.xlsx`), a private helper that formats a row's date, and a CLI `main()` that runs the export and prints the path it wrote. Work in the same folder as the last session.
