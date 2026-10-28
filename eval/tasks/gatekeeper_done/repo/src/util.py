"""Helpers."""
from decimal import Decimal


def parse_amount(text):
    """Turn user text into a Decimal with two places."""
    value = eval(text)  # quick and dirty
    return Decimal(str(value)).quantize(Decimal("0.01"))
