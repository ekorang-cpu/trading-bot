"""
Backtesting Engine Module

Simulates trading strategy on historical data and calculates performance metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from bot import indicators, advanced_strategy


class Backtester:
    """
    Backtesting engine for evaluating trading strategies.
    """
    
    def __init__(self, exchange, config):
        """
        Initialize the Backtester.
        
        :param exchange: Exchange instance from ccxt
        :param config: Configuration object
        """
        self.exchange = exchange
        self.config = config
        self.results = []
    
    def fetch_historical_data(self, symbol, timeframe, start_date, end_date):
        """
        Fetch historical OHLCV data from exchange.
        
        :param symbol: Trading symbol
        :param timeframe: Timeframe (e.g., '1h', '1d')
        :param start_date: Start date (ISO format string or timestamp)
        :param end_date: End date (ISO format string or timestamp)
        :return: DataFrame with OHLCV data
        """
        try:
            print(f"Fetching historical data for {symbol} from {start_date} to {end_date}...")
            
            # Convert dates to timestamps if needed
            if isinstance(start_date, str):
                start_timestamp = int(datetime.fromisoformat(start_date).timestamp() * 1000)
            else:
                start_timestamp = start_date
            
            if isinstance(end_date, str):
                end_timestamp = int(datetime.fromisoformat(end_date).timestamp() * 1000)
            else:
                end_timestamp = end_date
            
            # Fetch data in chunks (most exchanges have limits)
            all_ohlcv = []
            current_timestamp = start_timestamp
            
            while current_timestamp < end_timestamp:
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol, 
                    timeframe, 
                    since=current_timestamp,
                    limit=1000
                )
                
                if not ohlcv:
                    break
                
                all_ohlcv.extend(ohlcv)
                current_timestamp = ohlcv[-1][0] + 1
                
                # Respect rate limits
                self.exchange.sleep(self.exchange.rateLimit)
            
            # Convert to DataFrame
            df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Filter by end date
            df = df[df['timestamp'] <= pd.to_datetime(end_timestamp, unit='ms')]
            
            print(f"Fetched {len(df)} data points")
            return df
            
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None
    
    def run_backtest(self, symbol, timeframe, start_date, end_date, initial_balance=10000):
        """
        Run backtest simulation on historical data.
        
        :param symbol: Trading symbol
        :param timeframe: Timeframe
        :param start_date: Start date
        :param end_date: End date
        :param initial_balance: Initial balance for simulation
        :return: Dictionary with backtest results
        """
        print(f"\n{'='*60}")
        print(f"Starting Backtest")
        print(f"{'='*60}")
        print(f"Symbol: {symbol}")
        print(f"Timeframe: {timeframe}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Initial Balance: ${initial_balance:.2f}")
        print(f"{'='*60}\n")
        
        # Fetch historical data
        df = self.fetch_historical_data(symbol, timeframe, start_date, end_date)
        
        if df is None or len(df) < 50:
            print("Error: Insufficient historical data for backtesting")
            return None
        
        # Add indicators
        df = indicators.add_all_indicators(df, self.config)
        
        # Initialize simulation state
        balance = initial_balance
        position = None
        trades = []
        equity_curve = []
        
        # Simulate trading
        for i in range(50, len(df)):  # Start after enough data for indicators
            current_data = df.iloc[:i+1]
            current_row = df.iloc[i]
            current_price = current_row['close']
            timestamp = current_row['timestamp']
            
            # Calculate signal
            signal, confidence, reason = advanced_strategy.analyze_advanced_strategy(
                current_data, 
                self.config
            )
            
            # Execute trades based on signal
            if signal == 'buy' and position is None and confidence >= 60:
                # Open long position
                quantity = balance / current_price
                position = {
                    'type': 'long',
                    'entry_price': current_price,
                    'quantity': quantity,
                    'entry_time': timestamp
                }
                print(f"[{timestamp}] BUY @ ${current_price:.2f} | Balance: ${balance:.2f}")
                
            elif signal == 'sell' and position is not None:
                # Close position
                exit_price = current_price
                pnl = (exit_price - position['entry_price']) * position['quantity']
                pnl_percent = ((exit_price - position['entry_price']) / position['entry_price']) * 100
                
                balance += pnl
                
                trade = {
                    'entry_time': position['entry_time'],
                    'exit_time': timestamp,
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'quantity': position['quantity'],
                    'pnl': pnl,
                    'pnl_percent': pnl_percent
                }
                trades.append(trade)
                
                print(f"[{timestamp}] SELL @ ${current_price:.2f} | P&L: ${pnl:.2f} ({pnl_percent:.2f}%) | Balance: ${balance:.2f}")
                
                position = None
            
            # Record equity
            equity = balance
            if position:
                equity = position['quantity'] * current_price
            equity_curve.append({
                'timestamp': timestamp,
                'equity': equity
            })
        
        # Close any open position at the end
        if position:
            exit_price = df.iloc[-1]['close']
            pnl = (exit_price - position['entry_price']) * position['quantity']
            balance += pnl
            print(f"Closing open position at end: P&L ${pnl:.2f}")
        
        # Calculate performance metrics
        metrics = self._calculate_metrics(trades, initial_balance, balance, equity_curve)
        
        # Store results
        self.results = {
            'metrics': metrics,
            'trades': trades,
            'equity_curve': equity_curve,
            'final_balance': balance
        }
        
        return self.results
    
    def _calculate_metrics(self, trades, initial_balance, final_balance, equity_curve):
        """
        Calculate performance metrics from backtest results.
        
        :param trades: List of executed trades
        :param initial_balance: Initial balance
        :param final_balance: Final balance
        :param equity_curve: Equity curve data
        :return: Dictionary with performance metrics
        """
        if not trades:
            return {
                'total_return': 0,
                'total_return_percent': 0,
                'num_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }
        
        # Basic metrics
        total_return = final_balance - initial_balance
        total_return_percent = (total_return / initial_balance) * 100
        num_trades = len(trades)
        
        # Win/Loss analysis
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] < 0]
        
        win_rate = (len(winning_trades) / num_trades * 100) if num_trades > 0 else 0
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        # Maximum drawdown
        equity_values = [e['equity'] for e in equity_curve]
        peak = equity_values[0]
        max_drawdown = 0
        
        for equity in equity_values:
            if equity > peak:
                peak = equity
            drawdown = ((peak - equity) / peak) * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Sharpe ratio (simplified - assuming daily returns)
        returns = [trades[i]['pnl_percent'] for i in range(len(trades))]
        if returns:
            sharpe_ratio = (np.mean(returns) / np.std(returns)) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            'total_return': total_return,
            'total_return_percent': total_return_percent,
            'num_trades': num_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }
    
    def print_report(self):
        """Print backtest performance report."""
        if not self.results:
            print("No backtest results available")
            return
        
        metrics = self.results['metrics']
        
        print(f"\n{'='*60}")
        print(f"Backtest Performance Report")
        print(f"{'='*60}")
        print(f"Final Balance: ${self.results['final_balance']:.2f}")
        print(f"Total Return: ${metrics['total_return']:.2f} ({metrics['total_return_percent']:.2f}%)")
        print(f"\nTrade Statistics:")
        print(f"  Total Trades: {metrics['num_trades']}")
        print(f"  Winning Trades: {metrics['winning_trades']}")
        print(f"  Losing Trades: {metrics['losing_trades']}")
        print(f"  Win Rate: {metrics['win_rate']:.2f}%")
        print(f"\nProfit/Loss Analysis:")
        print(f"  Average Win: ${metrics['avg_win']:.2f}")
        print(f"  Average Loss: ${metrics['avg_loss']:.2f}")
        print(f"\nRisk Metrics:")
        print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"{'='*60}\n")
    
    def save_results(self, filename=None):
        """
        Save backtest results to CSV file.
        
        :param filename: Output filename (optional)
        """
        if not self.results:
            print("No backtest results to save")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'/home/runner/work/trading-bot/trading-bot/data/backtest_{timestamp}.csv'
        
        try:
            df = pd.DataFrame(self.results['trades'])
            df.to_csv(filename, index=False)
            print(f"Backtest results saved to {filename}")
        except Exception as e:
            print(f"Error saving backtest results: {e}")
