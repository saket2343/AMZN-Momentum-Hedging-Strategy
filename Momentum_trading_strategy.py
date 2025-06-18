
from blueshift.api import (
    symbol, 
    order_target_percent, 
    schedule_function, 
    date_rules, 
    time_rules
)

def initialize(context):
    """
    Function to initialize strategy parameters and schedule rebalancing.
    """
    context.long_portfolio = [
        symbol('AMZN')
    ]

    context.lookback = 50  # Number of days to calculate momentum
    context.cash_buffer = 0.1  # 10% of capital in cash

    # Schedule rebalancing every month
    schedule_function(rebalance,
                      date_rules.month_start(days_offset=0),
                      time_rules.market_open(hours=2, minutes=30))

def compute_momentum(context, data):
    """
    Function to compute momentum of stocks in the portfolio.
    """
    momentum_scores = {}
    for stock in context.long_portfolio:
        hist = data.history(stock, 'close', context.lookback, '1d')  # Use `data.history()`
        if len(hist) > 1:
            momentum_scores[stock] = (hist.iloc[-1] - hist.iloc[0]) / hist.iloc[0]
        else:
            momentum_scores[stock] = 0
    return momentum_scores

def rebalance(context, data):
    """
    Function to rebalance portfolio based on momentum and risk management.
    """
    # Compute momentum scores
    momentum_scores = compute_momentum(context, data)
    
    # Sort stocks based on momentum (descending)
    sorted_stocks = sorted(momentum_scores, key=momentum_scores.get, reverse=True)
    
    selected_stocks = [stock for stock in sorted_stocks if momentum_scores[stock] > 0]
    
    if not selected_stocks:
        return  # Avoid trading if no stock has positive momentum
    
    # Allocate 90% capital equally among selected stocks
    allocation = (1.0 - context.cash_buffer) / len(selected_stocks)
    
    for stock in context.long_portfolio:
        if stock in selected_stocks:
            order_target_percent(stock, allocation)
        else:
            order_target_percent(stock, 0)  # Exit non-selected stocks