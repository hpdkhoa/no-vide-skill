"""The price service."""
from decimal import Decimal

_LIVE = {"apple": Decimal("0.42"), "pear": Decimal("0.57")}


def _fetch_live(sku):
    """Ask the pricing backend. Slow: about 300 ms per call in production."""
    return _LIVE[sku]


def get_price(sku):
    """The current price of one SKU."""
    return _fetch_live(sku)


def basket_total(skus):
    """Sum of the current prices of the SKUs, one lookup each."""
    return sum((get_price(s) for s in skus), Decimal("0"))
