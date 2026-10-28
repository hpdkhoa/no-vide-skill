from decimal import Decimal

from src.wallet import Wallet


def test_transfer_moves_money():
    a, b = Wallet(), Wallet()
    a.deposit(Decimal("5.00"))
    assert a.transfer(b, Decimal("2.00")) == (Decimal("3.00"), Decimal("2.00"))
