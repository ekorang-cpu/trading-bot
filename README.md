# Python Predictive Trading Bot

A sophisticated, production-ready cryptocurrency trading bot that uses advanced technical analysis, risk management, and portfolio tracking to automate trading on multiple exchanges.

## 🚀 Key Features

### Core Features
- **Multi-Exchange Support**: Connects to 100+ exchanges via the `ccxt` library
- **Advanced Technical Analysis**: Multiple indicators including RSI, MACD, Bollinger Bands, and EMA
- **Multi-Indicator Strategy**: Generates signals only when multiple indicators align
- **Comprehensive Risk Management**: Stop-loss, take-profit, position sizing, and daily limits
- **Portfolio Tracking**: Real-time P&L tracking, position management, and trade history
- **Advanced Logging**: Detailed logging with file rotation and CSV export
- **Backtesting Engine**: Test strategies on historical data with performance metrics
- **Graceful Shutdown**: Safe shutdown handling to prevent incomplete operations

### Risk Management Features
- ⚠️ **Stop-Loss Protection**: Automatically exit positions at configurable loss threshold (default: 2%)
- ✅ **Take-Profit**: Lock in gains at configurable profit target (default: 5%)
- 💰 **Position Sizing**: Calculate safe trade sizes based on account balance (default: 10% per trade)
- 📊 **Daily Loss Limits**: Stop trading if daily losses exceed threshold (default: 5%)
- 🔢 **Trade Frequency Limits**: Prevent overtrading with max trades per day (default: 10)
- 🛑 **Emergency Stop**: Manual kill switch to halt all trading immediately

### Technical Indicators
- **RSI (Relative Strength Index)**: Identify overbought/oversold conditions
- **MACD (Moving Average Convergence Divergence)**: Trend-following momentum indicator
- **Bollinger Bands**: Volatility and price level assessment
- **EMA (Exponential Moving Average)**: Weighted moving averages for trend analysis
- **SMA (Simple Moving Average)**: Traditional moving average for trend detection

## 📋 Technology Stack

- **Language**: Python 3.8+
- **Key Libraries**:
  - `ccxt`: Multi-exchange API interaction
  - `pandas`: Data manipulation and analysis
  - `numpy`: Numerical computations
  - `ta`: Technical analysis library
  - `matplotlib`: Data visualization
  - `python-dotenv`: Environment variable management

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ekorang-cpu/trading-bot.git
   cd trading-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**:
   ```bash
   cp config.example.py config.py
   ```
   Edit `config.py` with your settings (see Configuration section below).

## ⚙️ Configuration

### Basic Configuration

Edit `config.py` with your exchange credentials and preferences:

```python
# Exchange and credentials
EXCHANGE_ID = 'binance'
API_KEY = 'your_api_key_here'
SECRET_KEY = 'your_secret_key_here'
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1h'

# Strategy selection
USE_ADVANCED_STRATEGY = True  # Use multi-indicator strategy
```

### Risk Management Configuration

Configure risk parameters to match your risk tolerance:

```python
# Conservative profile (low risk)
STOP_LOSS_PERCENT = 1.0        # Stop at 1% loss
TAKE_PROFIT_PERCENT = 3.0      # Take profit at 3%
POSITION_SIZE_PERCENT = 5.0    # Use 5% per trade
MAX_DAILY_LOSS_PERCENT = 2.0   # Stop at 2% daily loss
MAX_TRADES_PER_DAY = 5

# Moderate profile (balanced)
STOP_LOSS_PERCENT = 2.0
TAKE_PROFIT_PERCENT = 5.0
POSITION_SIZE_PERCENT = 10.0
MAX_DAILY_LOSS_PERCENT = 5.0
MAX_TRADES_PER_DAY = 10

# Aggressive profile (higher risk)
STOP_LOSS_PERCENT = 3.0
TAKE_PROFIT_PERCENT = 8.0
POSITION_SIZE_PERCENT = 20.0
MAX_DAILY_LOSS_PERCENT = 10.0
MAX_TRADES_PER_DAY = 20
```

### Technical Indicator Settings

Customize indicator parameters:

```python
# RSI settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# MACD settings
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands
BB_PERIOD = 20
BB_STD = 2
```

### Logging Configuration

```python
LOG_LEVEL = 'INFO'           # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True           # Save logs to files
LOG_TRADES_TO_CSV = True     # Export trades to CSV
```

## 🚀 Usage

### Running the Bot

**Production mode** (with real trading - use with caution):
```bash
python bot/main.py
```

**Demo mode** (default - simulates trades without executing):
The bot runs in demo mode by default. To enable live trading, uncomment the order execution code in `bot/main.py`.

⚠️ **Warning**: Always test with small amounts first and use sandbox/testnet modes when available!

### Running a Backtest

To test your strategy on historical data:

```python
from bot.backtester import Backtester
from bot import exchange_interface
import config

# Initialize
exchange = exchange_interface.get_exchange()
backtester = Backtester(exchange, config)

# Run backtest
results = backtester.run_backtest(
    symbol='BTC/USDT',
    timeframe='1h',
    start_date='2024-01-01',
    end_date='2024-12-31',
    initial_balance=10000
)

# View results
backtester.print_report()
backtester.save_results()  # Save to CSV
```

### Using Individual Modules

**Calculate Technical Indicators**:
```python
from bot import indicators
import pandas as pd

# Calculate RSI
rsi = indicators.calculate_rsi(prices, period=14)

# Calculate MACD
macd = indicators.calculate_macd(prices)

# Add all indicators to DataFrame
df = indicators.add_all_indicators(df, config)
```

**Risk Management**:
```python
from bot.risk_manager import RiskManager

risk_manager = RiskManager(config)

# Check if trading is allowed
can_trade, reason = risk_manager.can_trade(balance=10000)

# Calculate position size
quantity = risk_manager.calculate_position_size(balance=10000, price=50000)

# Check stop-loss/take-profit
if risk_manager.check_stop_loss('BTC/USDT', current_price):
    # Exit position
    pass
```

**Portfolio Tracking**:
```python
from bot.portfolio import Portfolio

portfolio = Portfolio(exchange)

# Get portfolio summary
summary = portfolio.get_portfolio_summary()
print(f"Total Balance: ${summary['total_balance']:.2f}")
print(f"Win Rate: {summary['win_rate']:.1f}%")

# Export trade history
portfolio.export_trade_history_csv()
```

## 📊 Monitoring and Logs

The bot generates several log files in the `logs/` directory:

- `trading_bot.log`: Main application log with all activities
- `trades.log`: Detailed trade execution log
- `signals.log`: Strategy signals and analysis
- `errors.log`: Error and exception log
- `trades.csv`: Trade history in CSV format for analysis

## 🔒 Safety Features and Best Practices

### Built-in Safety Features
1. **Emergency Stop**: Press Ctrl+C for graceful shutdown
2. **Risk Limits**: Automatic trading halt when limits are exceeded
3. **Position Tracking**: Always knows your current positions
4. **Error Handling**: Comprehensive error catching and logging
5. **Demo Mode**: Test safely before live trading

### Best Practices

✅ **DO**:
- Start with demo/paper trading mode
- Use sandbox/testnet mode when available
- Set conservative risk limits initially
- Monitor logs regularly
- Test strategies with backtesting first
- Keep API keys secure (use environment variables)
- Start with small amounts
- Review and adjust strategy parameters based on performance

❌ **DON'T**:
- Trade with money you can't afford to lose
- Use high leverage without experience
- Ignore risk management settings
- Trade without understanding the strategy
- Commit API keys to version control
- Run multiple instances on the same account
- Make impulsive parameter changes

### Security Recommendations

1. **API Key Security**:
   - Store keys in environment variables or secure vault
   - Use IP whitelist on exchange if available
   - Enable only required permissions (no withdrawal rights)
   - Rotate keys regularly

2. **Risk Management**:
   - Always use stop-loss orders
   - Never risk more than 1-2% per trade
   - Limit total exposure to 10-20% of capital
   - Set daily loss limits

3. **Monitoring**:
   - Check logs daily
   - Monitor portfolio performance
   - Set up alerts for errors
   - Review trade history regularly

## 📈 Performance Metrics

The backtesting engine provides comprehensive metrics:

- **Total Return**: Overall profit/loss
- **Win Rate**: Percentage of profitable trades
- **Average Win/Loss**: Average profit and loss per trade
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return metric
- **Trade Count**: Total number of trades executed

## 🗂️ Project Structure

```
trading-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py                    # Main bot entry point
│   ├── exchange_interface.py      # Exchange API wrapper
│   ├── strategy.py                # Simple MA strategy
│   ├── advanced_strategy.py       # Multi-indicator strategy
│   ├── indicators.py              # Technical indicators
│   ├── portfolio.py               # Portfolio tracking
│   ├── risk_manager.py            # Risk management
│   ├── backtester.py              # Backtesting engine
│   └── logger.py                  # Logging system
├── logs/                          # Log files (created at runtime)
├── data/                          # Trade history and state
├── notebooks/                     # Jupyter notebooks for analysis
├── config.example.py              # Example configuration
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## ⚖️ Disclaimer

**This software is for educational purposes only. Trading cryptocurrencies carries significant risk of loss.**

- Past performance does not guarantee future results
- The authors are not responsible for any financial losses
- Always do your own research (DYOR)
- Only invest what you can afford to lose
- This is not financial advice

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review logs for error messages

## 🔄 Updates and Roadmap

Future enhancements:
- Machine learning models for prediction
- Multi-symbol trading support
- Web dashboard for monitoring
- Mobile notifications
- Advanced order types (limit, OCO)
- Exchange arbitrage strategies
- Social sentiment analysis integration

---

**Remember**: Always test thoroughly before risking real money. Start small and scale up gradually as you gain confidence in the system.