"""A shopping cart. Prices are in cents."""


def total(lines, discount_percent=0):
    """Sum of quantity * unit price, then the discount, rounded to whole cents."""
    subtotal = sum(qty * unit for qty, unit in lines)
    return int(subtotal * (1 - discount_percent / 100))
