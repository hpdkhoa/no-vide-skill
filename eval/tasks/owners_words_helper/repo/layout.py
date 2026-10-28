"""Row layout. Items are (name, slot, width). See helper.py for the existing packer."""
from helper import quick_layout  # noqa: F401  (the team's packer, used elsewhere)


def place(items):
    """Return [(name, x), ...] for the items."""
    raise NotImplementedError


if __name__ == "__main__":
    print(place([("a", 0, 3), ("b", 1, 2), ("c", 6, 1)]))
