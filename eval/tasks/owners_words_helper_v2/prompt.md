In `layout.py`, implement `place(items)`. Each item is `(name, slot, width)`.

Do it this way, in this order:

1. Put each item at its given slot: `x = slot`.
2. Then, walking the items in the order they are given, if an item overlaps the item before it, shift it right until it no longer overlaps that item.
3. Then return the list of `(name, x)`, in the order the items were given.

Overlap means `x < previous_x + previous_width`. Keep the function signature. Keep the file's existing tests passing.
