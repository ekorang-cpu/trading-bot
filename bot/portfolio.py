"""
Portfolio Management Module

This module tracks account balance, positions, and calculates P&L.
"""

import json
import os
from datetime import datetime
import pandas as pd


class Portfolio:
    """
    Manages portfolio tracking including balance, positions, and P&L.
    """
    
    def __init__(self, exchange):
        """
        Initialize the Portfolio Manager.
        
        :param exchange: Exchange instance from ccxt
        """
        self.exchange = exchange
        self.trade_history = []
        self.open_positions = {}
        
        # Load trade history if exists
        self._load_trade_history()
    
    def _load_trade_history(self):
        """Load trade history from file."""
        history_file = '/home/runner/work/trading-bot/trading-bot/data/trade_history.json'
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    self.trade_history = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load trade history: {e}")
    
    def _save_trade_history(self):
        """Save trade history to file."""
        os.makedirs('/home/runner/work/trading-bot/trading-bot/data', exist_ok=True)
        history_file = '/home/runner/work/trading-bot/trading-bot/data/trade_history.json'
        try:
            with open(history_file, 'w') as f:
                json.dump(self.trade_history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save trade history: {e}")
    
    def fetch_balance(self):
        """
        Fetch current account balance from exchange.
        
        :return: Dictionary with balance information or None on error
        """
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return None
    
    def get_available_balance(self, currency='USDT'):
        """
        Get available balance for a specific currency.
        
        :param currency: Currency symbol (default: USDT)
        :return: Available balance or 0 on error
        """
        balance = self.fetch_balance()
        if balance and currency in balance:
            return balance[currency].get('free', 0)
        return 0
    
    def get_total_balance(self, currency='USDT'):
        """
        Get total balance (including locked) for a specific currency.
        
        :param currency: Currency symbol (default: USDT)
        :return: Total balance or 0 on error
        """
        balance = self.fetch_balance()
        if balance and currency in balance:
            return balance[currency].get('total', 0)
        return 0
    
    def add_position(self, symbol, side, entry_price, quantity, timestamp=None):
        """
        Add an open position to track.
        
        :param symbol: Trading symbol
        :param side: 'buy' or 'sell'
        :param entry_price: Entry price
        :param quantity: Quantity
        :param timestamp: Timestamp (optional)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        self.open_positions[symbol] = {
            'side': side,
            'entry_price': entry_price,
            'quantity': quantity,
            'timestamp': timestamp
        }
    
    def close_position(self, symbol, exit_price, timestamp=None):
        """
        Close a position and record the trade.
        
        :param symbol: Trading symbol
        :param exit_price: Exit price
        :param timestamp: Timestamp (optional)
        :return: P&L of the closed trade or None if position doesn't exist
        """
        if symbol not in self.open_positions:
            print(f"Warning: No open position for {symbol}")
            return None
        
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        quantity = position['quantity']
        side = position['side']
        
        # Calculate P&L
        if side == 'buy':
            pnl = (exit_price - entry_price) * quantity
            pnl_percent = ((exit_price - entry_price) / entry_price) * 100
        else:  # sell/short position
            pnl = (entry_price - exit_price) * quantity
            pnl_percent = ((entry_price - exit_price) / entry_price) * 100
        
        # Record trade
        trade = {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'quantity': quantity,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'entry_time': position['timestamp'],
            'exit_time': timestamp
        }
        
        self.trade_history.append(trade)
        self._save_trade_history()
        
        # Remove from open positions
        del self.open_positions[symbol]
        
        return pnl
    
    def calculate_unrealized_pnl(self, current_prices):
        """
        Calculate unrealized P&L for all open positions.
        
        :param current_prices: Dictionary of symbol: current_price
        :return: Dictionary with unrealized P&L per position
        """
        unrealized_pnl = {}
        
        for symbol, position in self.open_positions.items():
            if symbol not in current_prices:
                continue
            
            entry_price = position['entry_price']
            quantity = position['quantity']
            side = position['side']
            current_price = current_prices[symbol]
            
            if side == 'buy':
                pnl = (current_price - entry_price) * quantity
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
            else:  # sell/short
                pnl = (entry_price - current_price) * quantity
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
            
            unrealized_pnl[symbol] = {
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'current_price': current_price
            }
        
        return unrealized_pnl
    
    def calculate_realized_pnl(self, start_date=None, end_date=None):
        """
        Calculate realized P&L from closed trades.
        
        :param start_date: Start date for filtering (ISO format string)
        :param end_date: End date for filtering (ISO format string)
        :return: Dictionary with total realized P&L and trade count
        """
        total_pnl = 0
        trade_count = 0
        winning_trades = 0
        losing_trades = 0
        
        for trade in self.trade_history:
            # Filter by date if specified
            if start_date and trade['exit_time'] < start_date:
                continue
            if end_date and trade['exit_time'] > end_date:
                continue
            
            total_pnl += trade['pnl']
            trade_count += 1
            
            if trade['pnl'] > 0:
                winning_trades += 1
            elif trade['pnl'] < 0:
                losing_trades += 1
        
        win_rate = (winning_trades / trade_count * 100) if trade_count > 0 else 0
        
        return {
            'total_pnl': total_pnl,
            'trade_count': trade_count,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate
        }
    
    def get_portfolio_summary(self, current_prices=None):
        """
        Get a comprehensive portfolio summary.
        
        :param current_prices: Dictionary of current prices for calculating unrealized P&L
        :return: Dictionary with portfolio information
        """
        balance = self.fetch_balance()
        
        # Get USDT balance (or main quote currency)
        available_balance = self.get_available_balance('USDT')
        total_balance = self.get_total_balance('USDT')
        
        # Calculate unrealized P&L
        unrealized_pnl_total = 0
        if current_prices:
            unrealized = self.calculate_unrealized_pnl(current_prices)
            unrealized_pnl_total = sum(pos['pnl'] for pos in unrealized.values())
        
        # Calculate realized P&L
        realized = self.calculate_realized_pnl()
        
        # Calculate total portfolio value
        portfolio_value = total_balance + unrealized_pnl_total
        
        return {
            'available_balance': available_balance,
            'total_balance': total_balance,
            'unrealized_pnl': unrealized_pnl_total,
            'realized_pnl': realized['total_pnl'],
            'portfolio_value': portfolio_value,
            'open_positions': len(self.open_positions),
            'total_trades': realized['trade_count'],
            'win_rate': realized['win_rate']
        }
    
    def export_trade_history_csv(self, filename=None):
        """
        Export trade history to CSV file.
        
        :param filename: Output filename (optional)
        """
        if not self.trade_history:
            print("No trade history to export")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'/home/runner/work/trading-bot/trading-bot/data/trades_{timestamp}.csv'
        
        try:
            df = pd.DataFrame(self.trade_history)
            df.to_csv(filename, index=False)
            print(f"Trade history exported to {filename}")
        except Exception as e:
            print(f"Error exporting trade history: {e}")
    
    def get_trade_history(self, limit=None):
        """
        Get trade history.
        
        :param limit: Maximum number of trades to return (most recent first)
        :return: List of trades
        """
        if limit:
            return self.trade_history[-limit:]
        return self.trade_history
