"""
Advanced Logging System Module

Implements comprehensive logging with:
- Trade logging
- Strategy signal logging
- Error logging
- Log rotation
- CSV export for analysis
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import csv


# Log directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')


class TradingLogger:
    """
    Advanced logging system for trading bot.
    """
    
    def __init__(self, config):
        """
        Initialize the trading logger.
        
        :param config: Configuration object with logging parameters
        """
        self.config = config
        
        # Get logging parameters
        self.log_level = getattr(config, 'LOG_LEVEL', 'INFO')
        self.log_to_file = getattr(config, 'LOG_TO_FILE', True)
        self.log_trades_to_csv = getattr(config, 'LOG_TRADES_TO_CSV', True)
        
        # Create logs directory
        self.log_dir = LOG_DIR
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize loggers
        self.main_logger = self._setup_main_logger()
        self.trade_logger = self._setup_trade_logger()
        self.signal_logger = self._setup_signal_logger()
        self.error_logger = self._setup_error_logger()
        
        # CSV trade log file
        if self.log_trades_to_csv:
            self.trade_csv_file = self._setup_trade_csv()
    
    def _setup_main_logger(self):
        """Setup main application logger."""
        logger = logging.getLogger('trading_bot')
        logger.setLevel(getattr(logging, self.log_level))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.log_level))
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler with daily rotation
        if self.log_to_file:
            file_handler = TimedRotatingFileHandler(
                os.path.join(self.log_dir, 'trading_bot.log'),
                when='midnight',
                interval=1,
                backupCount=30  # Keep 30 days of logs
            )
            file_handler.setLevel(getattr(logging, self.log_level))
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        
        return logger
    
    def _setup_trade_logger(self):
        """Setup trade-specific logger."""
        logger = logging.getLogger('trading_bot.trades')
        logger.setLevel(logging.INFO)
        
        if self.log_to_file:
            file_handler = TimedRotatingFileHandler(
                os.path.join(self.log_dir, 'trades.log'),
                when='midnight',
                interval=1,
                backupCount=90  # Keep 90 days of trade logs
            )
            file_format = logging.Formatter(
                '%(asctime)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        
        return logger
    
    def _setup_signal_logger(self):
        """Setup signal-specific logger."""
        logger = logging.getLogger('trading_bot.signals')
        logger.setLevel(logging.INFO)
        
        if self.log_to_file:
            file_handler = TimedRotatingFileHandler(
                os.path.join(self.log_dir, 'signals.log'),
                when='midnight',
                interval=1,
                backupCount=30
            )
            file_format = logging.Formatter(
                '%(asctime)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        
        return logger
    
    def _setup_error_logger(self):
        """Setup error-specific logger."""
        logger = logging.getLogger('trading_bot.errors')
        logger.setLevel(logging.ERROR)
        
        if self.log_to_file:
            file_handler = RotatingFileHandler(
                os.path.join(self.log_dir, 'errors.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(exc_info)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        
        return logger
    
    def _setup_trade_csv(self):
        """Setup CSV file for trade logging."""
        csv_file = os.path.join(self.log_dir, 'trades.csv')
        
        # Create file with headers if it doesn't exist
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'symbol', 'side', 'price', 'quantity', 
                    'value', 'status', 'order_id', 'pnl', 'balance'
                ])
        
        return csv_file
    
    def info(self, message):
        """Log info message."""
        self.main_logger.info(message)
    
    def warning(self, message):
        """Log warning message."""
        self.main_logger.warning(message)
    
    def error(self, message, exc_info=False):
        """Log error message."""
        self.main_logger.error(message, exc_info=exc_info)
        self.error_logger.error(message, exc_info=exc_info)
    
    def debug(self, message):
        """Log debug message."""
        self.main_logger.debug(message)
    
    def log_trade(self, symbol, side, price, quantity, value=None, status='executed', 
                  order_id=None, pnl=None, balance=None):
        """
        Log a trade execution.
        
        :param symbol: Trading symbol
        :param side: 'buy' or 'sell'
        :param price: Execution price
        :param quantity: Quantity traded
        :param value: Total value (optional)
        :param status: Trade status (default: 'executed')
        :param order_id: Exchange order ID (optional)
        :param pnl: Profit/loss for the trade (optional)
        :param balance: Account balance after trade (optional)
        """
        if value is None:
            value = price * quantity
        
        timestamp = datetime.now().isoformat()
        
        # Log to trade logger
        log_message = (
            f"TRADE | {symbol} | {side.upper()} | "
            f"Price: ${price:.2f} | Qty: {quantity:.6f} | "
            f"Value: ${value:.2f}"
        )
        
        if pnl is not None:
            log_message += f" | P&L: ${pnl:.2f}"
        if balance is not None:
            log_message += f" | Balance: ${balance:.2f}"
        if order_id:
            log_message += f" | Order: {order_id}"
        
        self.trade_logger.info(log_message)
        
        # Log to CSV
        if self.log_trades_to_csv:
            try:
                with open(self.trade_csv_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        timestamp, symbol, side, price, quantity, 
                        value, status, order_id or '', pnl or '', balance or ''
                    ])
            except Exception as e:
                self.error(f"Error writing to trade CSV: {e}")
    
    def log_signal(self, symbol, signal, confidence, reason, indicators=None):
        """
        Log a trading signal.
        
        :param symbol: Trading symbol
        :param signal: Signal type ('buy', 'sell', 'hold')
        :param confidence: Confidence level (0-100)
        :param reason: Reason for the signal
        :param indicators: Dictionary of indicator values (optional)
        """
        log_message = (
            f"SIGNAL | {symbol} | {signal.upper()} | "
            f"Confidence: {confidence:.0f}% | {reason}"
        )
        
        if indicators:
            indicator_str = " | ".join([f"{k}: {v:.2f}" for k, v in indicators.items()])
            log_message += f" | Indicators: {indicator_str}"
        
        self.signal_logger.info(log_message)
    
    def log_risk_check(self, can_trade, reason, risk_summary=None):
        """
        Log risk management check results.
        
        :param can_trade: Whether trading is allowed
        :param reason: Reason for the decision
        :param risk_summary: Dictionary with risk metrics (optional)
        """
        status = "ALLOWED" if can_trade else "BLOCKED"
        log_message = f"RISK CHECK | {status} | {reason}"
        
        if risk_summary:
            log_message += f" | Daily trades: {risk_summary.get('daily_trades', 0)}"
            log_message += f" | Open positions: {risk_summary.get('open_positions', 0)}"
        
        self.main_logger.info(log_message)
    
    def log_portfolio_update(self, portfolio_summary):
        """
        Log portfolio status update.
        
        :param portfolio_summary: Dictionary with portfolio information
        """
        log_message = (
            f"PORTFOLIO | Balance: ${portfolio_summary.get('total_balance', 0):.2f} | "
            f"Open Positions: {portfolio_summary.get('open_positions', 0)} | "
            f"Unrealized P&L: ${portfolio_summary.get('unrealized_pnl', 0):.2f} | "
            f"Realized P&L: ${portfolio_summary.get('realized_pnl', 0):.2f} | "
            f"Win Rate: {portfolio_summary.get('win_rate', 0):.1f}%"
        )
        self.main_logger.info(log_message)
    
    def log_bot_start(self, config_summary):
        """
        Log bot startup information.
        
        :param config_summary: Dictionary with configuration details
        """
        self.main_logger.info("="*60)
        self.main_logger.info("Trading Bot Started")
        self.main_logger.info("="*60)
        for key, value in config_summary.items():
            self.main_logger.info(f"{key}: {value}")
        self.main_logger.info("="*60)
    
    def log_bot_stop(self, reason="User requested"):
        """
        Log bot shutdown.
        
        :param reason: Reason for shutdown
        """
        self.main_logger.info("="*60)
        self.main_logger.info(f"Trading Bot Stopped: {reason}")
        self.main_logger.info("="*60)
