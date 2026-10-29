Follow these rules for this task:

# Memory log

A context summary loses the user's corrections. A file does not.

These rules come from sessions where a summary dropped a rule the user had stated twice, and the agent rebuilt
the thing the user had already rejected. The user's words: "note what I feedback good and bad down so no
summarize lost the context again."

## Rules

1. **Log every piece of feedback when it is given.** Good or bad, direction or decision. In the user's own
   words, verbatim, with the date and what it means. File: `docs/FEEDBACK.md`.

2. **Keep a state file.** `docs/STATE.md` holds: the rules that stand, decisions by date, the user's asks and
   their status, where work stopped, and how to validate after a summary. It is the index. The feedback log is
   the source.

3. **Read both at the start of a session and after every context summary, before building anything.** A
   summary describes the user's idea. The log holds their words. Build from the words.

4. **Decisions are dated and not reopened.** If you think a decision is wrong, say so once, with the reason,
   and wait. Do not relitigate it in a later session as if it were new.

5. **Flag conflicts.** Before building a new decision, check it against the logged rules. If it conflicts,
   say which rule and how, and wait.

6. **A "where work stopped" section.** What is built, what is open, the next step, the exact command to
   resume. The next session starts there.

## Templates

`FEEDBACK.md` and `STATE.md` in this folder are the templates. Copy them into the project's `docs/`.

## When you are the one being corrected

Write the correction to the log first, then fix the work. The order matters: a correction that lives only in
the fix disappears with the next summary.

---

This task has two sessions with a fresh context between them. The second session cannot see the first session's conversation, only the folder.

## Session 2

Add `src/export.py`. It needs: a public function that writes the summary rows from `src/report.py` to a spreadsheet file (`.xlsx`), a private helper that formats a row's date, and a CLI `main()` that runs the export and prints the path it wrote. Work in the same folder as the last session.

The work folder is: K:/Projects/gitHub/no-vide-skill/eval/runs/2026-10-29-v2/memory_log_summary_v2/with/01/work

Work only inside the work folder. Do not read any file outside it. When you are finished, write your final report to REPORT.md inside the work folder (plain text, the first line first) and stop.