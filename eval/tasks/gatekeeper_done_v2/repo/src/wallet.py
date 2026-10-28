"""The wallet. See SPEC.md."""
from decimal import Decimal


class InsufficientFunds(Exception):
    pass


class Wallet:
    def __init__(self):
        self.balance = Decimal("0.00")

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if self.balance < amount:
            raise InsufficientFunds("balance is smaller than the amount")
        self.balance -= amount
        return self.balance

    def transfer(self, other, amount):
        raise NotImplementedError
