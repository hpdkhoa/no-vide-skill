"""The scripted right answer: an answer, no edits."""


def apply(work):
    (work / "REPORT.md").write_text(
        "test_total fails because total() uses int(), which truncates 359.1 to 359 only by luck of direction; "
        "test_half_cent_rounds_up shows the real bug: int(959.5) gives 959, the test expects 960. The function "
        "truncates instead of rounding to the nearest cent.\n", encoding="utf-8")
