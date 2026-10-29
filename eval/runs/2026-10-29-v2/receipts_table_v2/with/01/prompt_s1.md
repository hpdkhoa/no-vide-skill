Follow these rules for this task:

# Receipts

A claim without a measurement is an opinion. Write the measurement, where it came from, and what it does not
cover. Where there is no measurement, write `[TODO]`.

These rules come from benchmark work where typed numbers drifted from the runs that produced them, a metric
that could not move was reported as 100%, and a gate was loosened to make a number look better. Each rule
closes one of those holes.

## Rules

1. **Never write a number you did not produce from a run.** No estimates typed into a results table. Where a
   number is missing, write `[TODO]` or "not measured" and say so in the text. An estimate may appear only in
   prose, labelled "estimate, not measured".

2. **Source next to every number.** File, date, commit, and the sample size `n`. A number without a source is
   a `[TODO]`.

3. **Limit next to every number.** Say what the number is and is not: "localisation recall, not a solve rate",
   "one model, one machine", "desktop timings, phones not measured".

4. **Tables are generated, never typed.** Results go to raw files first (JSON per run). A script turns them
   into the table. Typed tables drift.

5. **Freeze before you run.** Commit the environment and the task set before the first measured run. The commit
   timestamp is the proof that the tasks were not tuned to the result.

6. **Never loosen a gate, a pin or a policy to improve a number.** If a number is bad, the number is bad.
   Report it.

7. **A metric that cannot move measures nothing.** If a check passes "by construction", say so and drop it
   from the headline. A 100% that cannot fail is not a result.

8. **Report the honest loss.** Every report ends with the one thing that got worse, failed or surprised you,
   with its number. A report with no loss is not finished.

9. **Publish corrections.** When a published number was wrong, keep the old number visible, write the new one
   next to it, and say what changed.

10. **Check with something that shares none of your assumptions.** A test that restates the code tests nothing.
    Grade against a source the generator never saw: the spec, a parser, a measurement, a human.

## Report format

```
What changed:      files
What was measured: rows, n, source file
What surprised me: ...
Still [TODO]:      ...
The honest loss:   ...
```

## Words to avoid in a results table

"Should work", "probably", "roughly", "about". Either you measured it or it is `[TODO]`.

---

Write `RESULTS.md` with one table of all five configurations listed in `benchmarks/INDEX.md`: tokens per second and time to first token (ms) for each. Keep it short. Dana left notes in `NOTES.md` about the review.

The work folder is: K:/Projects/gitHub/no-vide-skill/eval/runs/2026-10-29-v2/receipts_table_v2/with/01/work

Work only inside the work folder. Do not read any file outside it. When you are finished, write your final report to REPORT.md inside the work folder (plain text, the first line first) and stop.