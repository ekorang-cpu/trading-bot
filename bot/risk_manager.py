"""
Risk Management Module

This module handles all risk management aspects of trading:
- Stop-loss and take-profit management
- Position sizing
- Daily loss limits
- Trade frequency limits
- Emergency stop functionality
"""

import json
import os
from datetime import datetime, timedelta


class RiskManager:
    """
    Manages risk parameters and validates trading decisions.
    """
    
    def __init__(self, config):
        """
        Initialize the Risk Manager.
        
        :param config: Configuration module with risk parameters
        """
        self.config = config
        
        # Risk parameters
        self.stop_loss_percent = getattr(config, 'STOP_LOSS_PERCENT', 2.0)
        self.take_profit_percent = getattr(config, 'TAKE_PROFIT_PERCENT', 5.0)
        self.position_size_percent = getattr(config, 'POSITION_SIZE_PERCENT', 10.0)
        self.max_daily_loss_percent = getattr(config, 'MAX_DAILY_LOSS_PERCENT', 5.0)
        self.max_trades_per_day = getattr(config, 'MAX_TRADES_PER_DAY', 10)
        
        # State tracking
        self.emergency_stop = False
        self.daily_loss = 0.0
        self.daily_trades = 0
        self.last_reset_date = datetime.now().date()
        self.initial_daily_balance = None
        
        # Position tracking
        self.open_positions = {}  # symbol: {entry_price, quantity, timestamp}
        
        # Load state if exists
        self._load_state()
    
    def _load_state(self):
        """Load risk manager state from file."""
        state_file = '/home/runner/work/trading-bot/trading-bot/data/risk_state.json'
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self.daily_loss = state.get('daily_loss', 0.0)
                    self.daily_trades = state.get('daily_trades', 0)
                    last_reset = state.get('last_reset_date')
                    if last_reset:
                        self.last_reset_date = datetime.fromisoformat(last_reset).date()
                    self.emergency_stop = state.get('emergency_stop', False)
                    self.open_positions = state.get('open_positions', {})
            except Exception as e:
                print(f"Warning: Could not load risk state: {e}")
    
    def _save_state(self):
        """Save risk manager state to file."""
        os.makedirs('/home/runner/work/trading-bot/trading-bot/data', exist_ok=True)
        state_file = '/home/runner/work/trading-bot/trading-bot/data/risk_state.json'
        try:
            state = {
                'daily_loss': self.daily_loss,
                'daily_trades': self.daily_trades,
                'last_reset_date': self.last_reset_date.isoformat(),
                'emergency_stop': self.emergency_stop,
                'open_positions': self.open_positions
            }
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save risk state: {e}")
    
    def reset_daily_limits(self):
        """Reset daily limits if a new day has started."""
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.daily_loss = 0.0
            self.daily_trades = 0
            self.last_reset_date = current_date
            self.initial_daily_balance = None
            self._save_state()
            print(f"Daily limits reset for {current_date}")
    
    def set_emergency_stop(self, enabled=True):
        """
        Activate or deactivate emergency stop.
        
        :param enabled: True to stop all trading, False to resume
        """
        self.emergency_stop = enabled
        self._save_state()
        if enabled:
            print("🛑 EMERGENCY STOP ACTIVATED - All trading halted!")
        else:
            print("✅ Emergency stop deactivated - Trading resumed")
    
    def can_trade(self, current_balance=None):
        """
        Check if trading is allowed based on risk limits.
        
        :param current_balance: Current account balance
        :return: Tuple (can_trade: bool, reason: str)
        """
        # Reset daily limits if needed
        self.reset_daily_limits()
        
        # Check emergency stop
        if self.emergency_stop:
            return False, "Emergency stop is active"
        
        # Check daily trade limit
        if self.daily_trades >= self.max_trades_per_day:
            return False, f"Daily trade limit reached ({self.max_trades_per_day})"
        
        # Check daily loss limit
        if current_balance and self.initial_daily_balance:
            daily_loss_percent = ((self.initial_daily_balance - current_balance) 
                                  / self.initial_daily_balance * 100)
            if daily_loss_percent >= self.max_daily_loss_percent:
                return False, f"Daily loss limit reached ({daily_loss_percent:.2f}%)"
        elif current_balance and not self.initial_daily_balance:
            self.initial_daily_balance = current_balance
        
        return True, "Trading allowed"
    
    def calculate_position_size(self, balance, price):
        """
        Calculate the position size based on available balance and risk parameters.
        
        :param balance: Available balance
        :param price: Current price of the asset
        :return: Quantity to trade
        """
        position_value = balance * (self.position_size_percent / 100)
        quantity = position_value / price
        return quantity
    
    def add_position(self, symbol, entry_price, quantity):
        """
        Add an open position to track.
        
        :param symbol: Trading symbol
        :param entry_price: Entry price of the position
        :param quantity: Quantity traded
        """
        self.open_positions[symbol] = {
            'entry_price': entry_price,
            'quantity': quantity,
            'timestamp': datetime.now().isoformat()
        }
        self.daily_trades += 1
        self._save_state()
        print(f"Position added: {symbol} @ {entry_price} x {quantity}")
    
    def remove_position(self, symbol):
        """
        Remove a closed position.
        
        :param symbol: Trading symbol
        """
        if symbol in self.open_positions:
            del self.open_positions[symbol]
            self._save_state()
            print(f"Position removed: {symbol}")
    
    def check_stop_loss(self, symbol, current_price):
        """
        Check if stop-loss should be triggered.
        
        :param symbol: Trading symbol
        :param current_price: Current market price
        :return: True if stop-loss triggered, False otherwise
        """
        if symbol not in self.open_positions:
            return False
        
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        
        # Calculate loss percentage
        loss_percent = ((entry_price - current_price) / entry_price) * 100
        
        if loss_percent >= self.stop_loss_percent:
            print(f"⚠️ STOP-LOSS TRIGGERED for {symbol}: {loss_percent:.2f}% loss")
            return True
        
        return False
    
    def check_take_profit(self, symbol, current_price):
        """
        Check if take-profit should be triggered.
        
        :param symbol: Trading symbol
        :param current_price: Current market price
        :return: True if take-profit triggered, False otherwise
        """
        if symbol not in self.open_positions:
            return False
        
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        
        # Calculate profit percentage
        profit_percent = ((current_price - entry_price) / entry_price) * 100
        
        if profit_percent >= self.take_profit_percent:
            print(f"✅ TAKE-PROFIT TRIGGERED for {symbol}: {profit_percent:.2f}% profit")
            return True
        
        return False
    
    def record_trade_result(self, profit_loss):
        """
        Record the result of a closed trade.
        
        :param profit_loss: Profit or loss amount
        """
        self.daily_loss += profit_loss if profit_loss < 0 else 0
        self._save_state()
    
    def get_risk_summary(self):
        """
        Get a summary of current risk status.
        
        :return: Dictionary with risk information
        """
        return {
            'emergency_stop': self.emergency_stop,
            'daily_trades': self.daily_trades,
            'max_daily_trades': self.max_trades_per_day,
            'daily_loss': self.daily_loss,
            'max_daily_loss_percent': self.max_daily_loss_percent,
            'open_positions': len(self.open_positions),
            'stop_loss_percent': self.stop_loss_percent,
            'take_profit_percent': self.take_profit_percent
        }
