# Wallet spec

- Balances and amounts are `Decimal` with two places. Never float.
- `deposit(amount)`: amount must be greater than zero, else `ValueError`. Adds to the balance.
- `withdraw(amount)`: amount must be greater than zero, else `ValueError`. If the balance is smaller than the
  amount, raise `InsufficientFunds`. Otherwise subtract and return the new balance.
- `transfer(other, amount)`: withdraw `amount` from this wallet and deposit it into `other`, with the same rules
  as `withdraw` and `deposit`. Return the pair `(self.balance, other.balance)`. If the withdraw fails, `other`
  must not change.
