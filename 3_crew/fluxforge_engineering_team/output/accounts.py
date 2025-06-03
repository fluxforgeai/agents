import time
from typing import Dict, List, Optional, Union

# Test implementation of get_share_price function
def get_share_price(symbol: str) -> float:
    """
    Returns the current stub share price for the given symbol.
    For test purposes only: Hardcoded for AAPL, TSLA, GOOGL.
    """
    prices = {
        'AAPL': 150.0,
        'TSLA': 200.0,
        'GOOGL': 2500.0
    }
    if symbol not in prices:
        raise ValueError(f"Unknown symbol: {symbol}")
    return prices[symbol]


class Account:
    def __init__(self, username: str, initial_deposit: float):
        """
        Initializes a new account for the user with a unique username and an initial deposit.
        - username: Unique identifier for the user.
        - initial_deposit: The initial amount of money deposited.
        """
        if initial_deposit <= 0:
            raise ValueError("Initial deposit must be greater than 0")
        
        self.username = username
        self.cash_balance = initial_deposit
        self.total_deposited = initial_deposit
        self.holdings = {}  # {symbol: quantity}
        self.transactions = []
        
        # Record initial deposit transaction
        self._record_transaction(
            transaction_type='Deposit',
            amount=initial_deposit
        )
    
    def deposit(self, amount: float) -> None:
        """
        Deposits funds into the account.
        - amount: The amount to deposit (must be > 0).
        Raises ValueError if amount <= 0.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than 0")
        
        self.cash_balance += amount
        self.total_deposited += amount
        self._record_transaction(
            transaction_type='Deposit',
            amount=amount
        )
    
    def withdraw(self, amount: float) -> None:
        """
        Withdraws funds from the account.
        - amount: The amount to withdraw.
        Raises ValueError if amount <= 0 or insufficient available balance.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than 0")
        
        if amount > self.cash_balance:
            raise ValueError(f"Insufficient funds. Available balance: {self.cash_balance}")
        
        self.cash_balance -= amount
        self._record_transaction(
            transaction_type='Withdraw',
            amount=amount
        )
    
    def buy(self, symbol: str, quantity: int) -> None:
        """
        Buys shares for the specified symbol.
        - symbol: The share ticker (e.g., 'AAPL').
        - quantity: Number of shares to buy (must be > 0).
        Uses get_share_price(symbol) for price.
        Raises ValueError for insufficient funds or invalid quantity.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        price = get_share_price(symbol)
        total_cost = price * quantity
        
        if total_cost > self.cash_balance:
            raise ValueError(f"Insufficient funds. Cost: {total_cost}, Available: {self.cash_balance}")
        
        self.cash_balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        
        self._record_transaction(
            transaction_type='Buy',
            symbol=symbol,
            quantity=quantity,
            price=price,
            amount=total_cost
        )
    
    def sell(self, symbol: str, quantity: int) -> None:
        """
        Sells shares for the specified symbol.
        - symbol: The share ticker.
        - quantity: Number of shares to sell (must be > 0).
        Uses get_share_price(symbol) for price.
        Raises ValueError if not enough shares held, or invalid quantity.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        current_holding = self.holdings.get(symbol, 0)
        if current_holding < quantity:
            raise ValueError(f"Insufficient shares. Holding: {current_holding}, Requested: {quantity}")
        
        price = get_share_price(symbol)
        total_proceeds = price * quantity
        
        self.cash_balance += total_proceeds
        self.holdings[symbol] -= quantity
        
        # Remove symbol from holdings if quantity is 0
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        self._record_transaction(
            transaction_type='Sell',
            symbol=symbol,
            quantity=quantity,
            price=price,
            amount=total_proceeds
        )
    
    def get_cash_balance(self) -> float:
        """
        Returns the current cash balance available in the account.
        """
        return self.cash_balance
    
    def get_holdings(self) -> dict:
        """
        Returns a dictionary: {symbol: quantity} of shares currently held.
        """
        return self.holdings.copy()
    
    def get_portfolio_value(self) -> float:
        """
        Returns the total value (cash + holdings, valued at current market prices) of the account.
        """
        total_value = self.cash_balance
        
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            total_value += price * quantity
        
        return total_value
    
    def get_profit_loss(self) -> float:
        """
        Returns the current profit or loss since the initial deposit (portfolio value minus total deposited, not counting withdrawals).
        """
        return self.get_portfolio_value() - self.total_deposited
    
    def get_transactions(self) -> list:
        """
        Returns a list of transactions performed (deposits, withdrawals, buys, sells).
        Each entry: dict with keys ('timestamp', 'type', 'symbol', 'quantity', 'price', 'amount', etc.).
        """
        return [tx.copy() for tx in self.transactions]
    
    def get_holding_at(self, timestamp: float) -> dict:
        """
        Returns the user's holdings at a specific Unix timestamp.
        Replays the transactions to provide the state at that point.
        """
        holdings_at_time = {}
        
        for tx in self.transactions:
            if tx['timestamp'] > timestamp:
                break
            
            if tx['type'] == 'Buy':
                symbol = tx['symbol']
                quantity = tx['quantity']
                holdings_at_time[symbol] = holdings_at_time.get(symbol, 0) + quantity
            elif tx['type'] == 'Sell':
                symbol = tx['symbol']
                quantity = tx['quantity']
                holdings_at_time[symbol] = holdings_at_time.get(symbol, 0) - quantity
                if holdings_at_time[symbol] == 0:
                    del holdings_at_time[symbol]
        
        return holdings_at_time
    
    def get_profit_loss_at(self, timestamp: float) -> float:
        """
        Returns the profit or loss as of a specific Unix timestamp.
        Calculates using the portfolio value and deposited amount up to that time.
        """
        cash_at_time = 0.0
        deposited_at_time = 0.0
        holdings_at_time = {}
        
        for tx in self.transactions:
            if tx['timestamp'] > timestamp:
                break
            
            if tx['type'] == 'Deposit':
                cash_at_time += tx['amount']
                deposited_at_time += tx['amount']
            elif tx['type'] == 'Withdraw':
                cash_at_time -= tx['amount']
            elif tx['type'] == 'Buy':
                cash_at_time -= tx['amount']
                symbol = tx['symbol']
                quantity = tx['quantity']
                holdings_at_time[symbol] = holdings_at_time.get(symbol, 0) + quantity
            elif tx['type'] == 'Sell':
                cash_at_time += tx['amount']
                symbol = tx['symbol']
                quantity = tx['quantity']
                holdings_at_time[symbol] = holdings_at_time.get(symbol, 0) - quantity
                if holdings_at_time[symbol] == 0:
                    del holdings_at_time[symbol]
        
        # Calculate portfolio value at that time
        portfolio_value_at_time = cash_at_time
        for symbol, quantity in holdings_at_time.items():
            price = get_share_price(symbol)
            portfolio_value_at_time += price * quantity
        
        return portfolio_value_at_time - deposited_at_time
    
    def _record_transaction(self, transaction_type: str, symbol: Optional[str] = None, 
                          quantity: Optional[int] = None, price: Optional[float] = None, 
                          amount: float = 0.0) -> None:
        """
        Records a transaction in the transaction history.
        """
        transaction = {
            'timestamp': time.time(),
            'type': transaction_type,
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'amount': amount,
            'balance': self.cash_balance
        }
        self.transactions.append(transaction)