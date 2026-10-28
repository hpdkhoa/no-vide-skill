from layout import place


def test_no_overlap_keeps_slots():
    assert place([("a", 0, 1), ("b", 5, 1)]) == [("a", 0), ("b", 5)]
