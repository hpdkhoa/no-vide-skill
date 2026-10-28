This task has two sessions with a fresh context between them. The second session cannot see the first session's conversation, only the folder.

## Session 1

Write `src/report.py` with a function that takes a list of `(date, amount)` rows and returns a one-line text summary (count and total).

Earlier in this session I corrected you three times. These corrections stand for the whole project:

1. "use logging, never print"
2. "function names in this project are verbs ending with `_report`, so this one is `summarize_report`"
3. "ask me before adding any dependency; do not add one on your own"

## Session 2

Add `src/export.py` with a function that writes the summary from `src/report.py` to a spreadsheet file. Work in the same folder as the last session.
