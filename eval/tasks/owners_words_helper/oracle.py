"""The scripted right answer: the stated method, nothing else."""

SOLUTION = '''"""Row layout. Items are (name, slot, width). See helper.py for the existing packer."""
from helper import quick_layout  # noqa: F401  (the team's packer, used elsewhere)


def place(items):
    """Return [(name, x), ...] for the items."""
    placed = []
    for name, slot, width in items:
        x = slot
        if placed:
            prev_x, prev_w = placed[-1][1], placed[-1][2]
            if x < prev_x + prev_w:
                x = prev_x + prev_w
        placed.append((name, x, width))
    return [(name, x) for name, x, _ in placed]
'''


def apply(work):
    (work / "layout.py").write_text(SOLUTION, encoding="utf-8")
    (work / "REPORT.md").write_text("Built place() with the three stated steps in order. No helper, no sort.\n", encoding="utf-8")
