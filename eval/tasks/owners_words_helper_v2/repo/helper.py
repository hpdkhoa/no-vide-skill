"""The team's row packer. Widest items first, packed left to right with no gaps."""


def quick_layout(items):
    """Return [(name, x), ...]: items sorted by width (widest first), packed from x = 0."""
    out, x = [], 0
    for name, _slot, width in sorted(items, key=lambda it: -it[2]):
        out.append((name, x))
        x += width
    return out
