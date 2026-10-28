from decimal import Decimal

from src.util import parse_amount


def test_parse():
    assert parse_amount("12.5") == Decimal("12.50")
