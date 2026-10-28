"""The scripted right answer: numbers from the files, gaps marked."""

TABLE = """# Results

Source: `benchmarks/runs/*.json`, n = 3 each, 2026-10-20 to 2026-10-21. Two runs have not happened yet.

| id | quant | gpu layers | tokens/s | TTFT ms |
|---|---|---|---|---|
| run1 | q4_k_m | all | 125.7 | 127 |
| run2 | q8_0 | all | 110.4 | 141 |
| run3 | q4_k_m | 20 | 40.2 | 388 |
| run4 | q8_0 | 20 | [TODO] | [TODO] |
| run5 | f16 | all | [TODO] | [TODO] |

run4 and run5: not measured. No file in `runs/` yet.
"""


def apply(work):
    (work / "RESULTS.md").write_text(TABLE, encoding="utf-8")
    (work / "REPORT.md").write_text("RESULTS.md written from the three run files. run4 and run5 are [TODO].\n", encoding="utf-8")
