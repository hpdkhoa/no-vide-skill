from cart import total


def test_plain():
    assert total([(2, 150), (1, 99)]) == 399


def test_total():
    # 10% off 399 cents is 359.1, which rounds to 359
    assert total([(2, 150), (1, 99)], discount_percent=10) == 359


def test_half_cent_rounds_up():
    # 5% off 1010 cents is 959.5, which rounds to 960
    assert total([(1, 1010)], discount_percent=5) == 960
