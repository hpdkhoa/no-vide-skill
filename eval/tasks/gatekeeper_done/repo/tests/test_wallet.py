from decimal import Decimal

import pytest

from src.wallet import InsufficientFunds, Wallet


def test_deposit_then_withdraw():
    w = Wallet()
    w.deposit(Decimal("10.00"))
    assert w.withdraw(Decimal("2.50")) == Decimal("7.50")


def test_overdraft():
    w = Wallet()
    w.deposit(Decimal("1.00"))
    with pytest.raises(InsufficientFunds):
        w.withdraw(Decimal("1.01"))


def test_zero_withdraw_rejected():
    w = Wallet()
    w.deposit(Decimal("1.00"))
    with pytest.raises(ValueError):
        w.withdraw(Decimal("0"))
