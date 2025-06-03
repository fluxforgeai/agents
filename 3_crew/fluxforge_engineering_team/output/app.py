import gradio as gr
from accounts import Account, get_share_price
import time
from datetime import datetime

# Global account instance (single user demo)
account = None

def create_account(username, initial_deposit):
    global account
    try:
        initial_deposit = float(initial_deposit)
        account = Account(username, initial_deposit)
        return f"Account created for {username} with initial deposit of ${initial_deposit:.2f}", update_dashboard()
    except ValueError as e:
        return f"Error: {str(e)}", ""

def deposit_funds(amount):
    if account is None:
        return "Error: Please create an account first", ""
    try:
        amount = float(amount)
        account.deposit(amount)
        return f"Successfully deposited ${amount:.2f}", update_dashboard()
    except ValueError as e:
        return f"Error: {str(e)}", ""

def withdraw_funds(amount):
    if account is None:
        return "Error: Please create an account first", ""
    try:
        amount = float(amount)
        account.withdraw(amount)
        return f"Successfully withdrew ${amount:.2f}", update_dashboard()
    except ValueError as e:
        return f"Error: {str(e)}", ""

def buy_shares(symbol, quantity):
    if account is None:
        return "Error: Please create an account first", ""
    try:
        quantity = int(quantity)
        price = get_share_price(symbol)
        account.buy(symbol, quantity)
        return f"Successfully bought {quantity} shares of {symbol} at ${price:.2f} per share", update_dashboard()
    except ValueError as e:
        return f"Error: {str(e)}", ""

def sell_shares(symbol, quantity):
    if account is None:
        return "Error: Please create an account first", ""
    try:
        quantity = int(quantity)
        price = get_share_price(symbol)
        account.sell(symbol, quantity)
        return f"Successfully sold {quantity} shares of {symbol} at ${price:.2f} per share", update_dashboard()
    except ValueError as e:
        return f"Error: {str(e)}", ""

def update_dashboard():
    if account is None:
        return "No account created yet"
    
    # Get current state
    cash_balance = account.get_cash_balance()
    portfolio_value = account.get_portfolio_value()
    profit_loss = account.get_profit_loss()
    holdings = account.get_holdings()
    
    # Format holdings
    holdings_str = "Holdings:\n"
    if holdings:
        for symbol, quantity in holdings.items():
            price = get_share_price(symbol)
            value = price * quantity
            holdings_str += f"  {symbol}: {quantity} shares @ ${price:.2f} = ${value:.2f}\n"
    else:
        holdings_str += "  No holdings\n"
    
    # Create dashboard summary
    dashboard = f"""
Account Summary for {account.username}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cash Balance: ${cash_balance:.2f}
Portfolio Value: ${portfolio_value:.2f}
Profit/Loss: ${profit_loss:+.2f} ({(profit_loss/account.total_deposited*100):+.1f}%)

{holdings_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return dashboard

def get_transactions_history():
    if account is None:
        return "No account created yet"
    
    transactions = account.get_transactions()
    if not transactions:
        return "No transactions yet"
    
    history = "Transaction History:\n"
    history += "=" * 80 + "\n"
    
    for tx in transactions:
        timestamp = datetime.fromtimestamp(tx['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        tx_type = tx['type']
        
        if tx_type in ['Deposit', 'Withdraw']:
            history += f"{timestamp} | {tx_type:8} | Amount: ${tx['amount']:.2f} | Balance: ${tx['balance']:.2f}\n"
        else:  # Buy or Sell
            history += f"{timestamp} | {tx_type:8} | {tx['symbol']:5} | {tx['quantity']:4} shares @ ${tx['price']:.2f} = ${tx['amount']:.2f} | Balance: ${tx['balance']:.2f}\n"
    
    return history

def get_available_prices():
    return """Available Stock Prices:
• AAPL: $150.00
• TSLA: $200.00
• GOOGL: $2,500.00"""

# Create Gradio interface
with gr.Blocks(title="Trading Account Demo") as demo:
    gr.Markdown("# 📈 Trading Account Management System")
    gr.Markdown("Demo trading platform with single user account")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Account Setup")
            username_input = gr.Textbox(label="Username", placeholder="Enter username")
            initial_deposit_input = gr.Number(label="Initial Deposit ($)", minimum=0.01)
            create_btn = gr.Button("Create Account", variant="primary")
            create_status = gr.Textbox(label="Status", interactive=False)
            
            gr.Markdown("### Cash Operations")
            deposit_amount = gr.Number(label="Deposit Amount ($)", minimum=0.01)
            deposit_btn = gr.Button("Deposit")
            
            withdraw_amount = gr.Number(label="Withdraw Amount ($)", minimum=0.01)
            withdraw_btn = gr.Button("Withdraw")
            
            cash_status = gr.Textbox(label="Transaction Status", interactive=False)
            
        with gr.Column(scale=1):
            gr.Markdown("### Trading Operations")
            stock_prices = gr.Textbox(value=get_available_prices(), label="Available Stocks", interactive=False)
            
            symbol_input = gr.Dropdown(choices=["AAPL", "TSLA", "GOOGL"], label="Stock Symbol")
            quantity_input = gr.Number(label="Quantity", minimum=1, precision=0)
            
            with gr.Row():
                buy_btn = gr.Button("Buy", variant="primary")
                sell_btn = gr.Button("Sell", variant="stop")
            
            trade_status = gr.Textbox(label="Trade Status", interactive=False)
            
        with gr.Column(scale=2):
            gr.Markdown("### Account Dashboard")
            dashboard_display = gr.Textbox(label="Account Summary", lines=10, interactive=False)
            refresh_btn = gr.Button("Refresh Dashboard")
            
            gr.Markdown("### Transaction History")
            history_display = gr.Textbox(label="All Transactions", lines=10, interactive=False)
            history_btn = gr.Button("View Transaction History")
    
    # Event handlers
    create_btn.click(
        create_account,
        inputs=[username_input, initial_deposit_input],
        outputs=[create_status, dashboard_display]
    )
    
    deposit_btn.click(
        deposit_funds,
        inputs=[deposit_amount],
        outputs=[cash_status, dashboard_display]
    )
    
    withdraw_btn.click(
        withdraw_funds,
        inputs=[withdraw_amount],
        outputs=[cash_status, dashboard_display]
    )
    
    buy_btn.click(
        buy_shares,
        inputs=[symbol_input, quantity_input],
        outputs=[trade_status, dashboard_display]
    )
    
    sell_btn.click(
        sell_shares,
        inputs=[symbol_input, quantity_input],
        outputs=[trade_status, dashboard_display]
    )
    
    refresh_btn.click(
        update_dashboard,
        outputs=[dashboard_display]
    )
    
    history_btn.click(
        get_transactions_history,
        outputs=[history_display]
    )

if __name__ == "__main__":
    demo.launch()