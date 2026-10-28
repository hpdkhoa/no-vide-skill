# Wallet spec

- Balances and amounts are `Decimal` with two places. Never float.
- `deposit(amount)`: amount must be greater than zero, else `ValueError`. Adds to the balance.
- `withdraw(amount)`: amount must be greater than zero, else `ValueError`. If the balance is smaller than the
  amount, raise `InsufficientFunds`. Otherwise subtract and return the new balance.
- `parse_amount(text)` turns user text like `"12.50"` into a `Decimal`. It must never execute the text.
