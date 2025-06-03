# accounts.py - Design Outline

## Overview

This module defines a self-contained Python backend for a trading simulation account management system. The key class is `Account`, which models a user's trading activity and funds, and supports deposit, withdrawal, trading, portfolio valuation and reporting operations, with all constraints and tracking as per requirements.

---

## Classes and Functions

### 1. Class: `Account`

#### Purpose:
Represents a single user's trading account, tracking cash, holdings, transaction history, and providing all required functionality.

#### Constructor
```python
def __init__(self, username: str, initial_deposit: float):
    """
    Initializes a new account for the user with a unique username and an initial deposit.
    - username: Unique identifier for the user.
    - initial_deposit: The initial amount of money deposited.
    """
```

#### Methods

```python
def deposit(self, amount: float) -> None:
    """
    Deposits funds into the account.
    - amount: The amount to deposit (must be > 0).
    Raises ValueError if amount <= 0.
    """

def withdraw(self, amount: float) -> None:
    """
    Withdraws funds from the account.
    - amount: The amount to withdraw.
    Raises ValueError if amount <= 0 or insufficient available balance.
    """

def buy(self, symbol: str, quantity: int) -> None:
    """
    Buys shares for the specified symbol.
    - symbol: The share ticker (e.g., 'AAPL').
    - quantity: Number of shares to buy (must be > 0).
    Uses get_share_price(symbol) for price.
    Raises ValueError for insufficient funds or invalid quantity.
    """

def sell(self, symbol: str, quantity: int) -> None:
    """
    Sells shares for the specified symbol.
    - symbol: The share ticker.
    - quantity: Number of shares to sell (must be > 0).
    Uses get_share_price(symbol) for price.
    Raises ValueError if not enough shares held, or invalid quantity.
    """

def get_cash_balance(self) -> float:
    """
    Returns the current cash balance available in the account.
    """

def get_holdings(self) -> dict:
    """
    Returns a dictionary: {symbol: quantity} of shares currently held.
    """

def get_portfolio_value(self) -> float:
    """
    Returns the total value (cash + holdings, valued at current market prices) of the account.
    """

def get_profit_loss(self) -> float:
    """
    Returns the current profit or loss since the initial deposit (portfolio value minus total deposited, not counting withdrawals).
    """

def get_transactions(self) -> list:
    """
    Returns a list of transactions performed (deposits, withdrawals, buys, sells).
    Each entry: dict with keys ('timestamp', 'type', 'symbol', 'quantity', 'price', 'amount', etc.).
    """

def get_holding_at(self, timestamp: float) -> dict:
    """
    Returns the user's holdings at a specific Unix timestamp.
    Replays the transactions to provide the state at that point.
    """

def get_profit_loss_at(self, timestamp: float) -> float:
    """
    Returns the profit or loss as of a specific Unix timestamp.
    Calculates using the portfolio value and deposited amount up to that time.
    """
```

---

### 2. Function: `get_share_price(symbol: str) -> float`

#### Purpose:
Returns the price of one share for the given symbol.
- Uses fixed stub/test prices for 'AAPL', 'TSLA', 'GOOGL'.
- Raises ValueError for unrecognized symbols during testing.

---

### 3. Class: `Transaction` (optional for structure; could also use dicts internally)

#### Purpose:
Represents a transaction, contains fields:
- timestamp: float (Unix time)
- type: str (Deposit/Withdraw/Buy/Sell)
- symbol: str or None
- quantity: int or None
- price: float or None
- amount: float (for cash events)
- balance: float (resulting cash balance)
  
---

## Example Structure

```python
# accounts.py

def get_share_price(symbol: str) -> float:
    """
    Returns the current stub share price for the given symbol.
    For test purposes only: Hardcoded for AAPL, TSLA, GOOGL.
    """

class Transaction:
    def __init__(...):
        # structured representation for transaction (optional)
        pass

class Account:
    def __init__(self, username: str, initial_deposit: float):
        pass
    
    def deposit(self, amount: float) -> None:
        pass

    def withdraw(self, amount: float) -> None:
        pass

    def buy(self, symbol: str, quantity: int) -> None:
        pass

    def sell(self, symbol: str, quantity: int) -> None:
        pass

    def get_cash_balance(self) -> float:
        pass

    def get_holdings(self) -> dict:
        pass

    def get_portfolio_value(self) -> float:
        pass

    def get_profit_loss(self) -> float:
        pass

    def get_transactions(self) -> list:
        pass

    def get_holding_at(self, timestamp: float) -> dict:
        pass

    def get_profit_loss_at(self, timestamp: float) -> float:
        pass
```

---

## Notes

- All validation (e.g., non-negative deposits, valid sell quantities, sufficient funds, no negative balances, etc.) enforced within methods.
- All transactions are timestamped and stored in an internal transaction log.
- All getter methods except for time-based report on current state.
- All monetary values are float for simplicity.
- The design supports extension to more symbols and more accurate price sources as needed.

---

## Usage Example (not required in code, for understanding)

```python
acct = Account(username="user1", initial_deposit=10000)
acct.deposit(5000)
acct.buy('AAPL', 10)
acct.sell('AAPL', 2)
balance = acct.get_cash_balance()
holdings = acct.get_holdings()
portfolio_value = acct.get_portfolio_value()
profit_loss = acct.get_profit_loss()
history = acct.get_transactions()
```

---

This completes the detailed design outline for the `accounts.py` module as required.