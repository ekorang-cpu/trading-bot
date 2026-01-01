# --- Exchange Settings ---
# Specify the ID of the exchange you want to use from the ccxt library.
# A list of all supported exchange IDs can be found here:
# https://github.com/ccxt/ccxt/wiki/Exchange-Markets
EXCHANGE_ID = 'binance'  # Example: 'binance', 'coinbasepro', 'kraken'

# --- API Credentials ---
# IMPORTANT: Keep these secret. Do not share them or commit them to a public repository.
# It is best practice to load these from environment variables or a secure vault.
API_KEY = 'YOUR_API_KEY_HERE'
SECRET_KEY = 'YOUR_SECRET_KEY_HERE'

# --- Trading Parameters ---
# The trading pair (symbol) you want the bot to trade.
SYMBOL = 'BTC/USDT'  # Example: 'ETH/USD'

# --- Strategy Settings ---
# Timeframe for market data (e.g., '1m', '5m', '1h', '1d').
TIMEFRAME = '1h'

# Amount of the base currency to use for each trade (deprecated - use POSITION_SIZE_PERCENT instead).
TRADE_AMOUNT = 100  # Example: a value in USDT for a 'BTC/USDT' pair.

# Use advanced multi-indicator strategy (True) or simple moving average strategy (False)
USE_ADVANCED_STRATEGY = True

# --- Risk Management Settings ---
# Stop loss at X% loss from entry price
STOP_LOSS_PERCENT = 2.0

# Take profit at X% gain from entry price
TAKE_PROFIT_PERCENT = 5.0

# Use X% of available balance per trade
POSITION_SIZE_PERCENT = 10.0

# Stop trading if daily loss exceeds X%
MAX_DAILY_LOSS_PERCENT = 5.0

# Maximum number of trades allowed per day
MAX_TRADES_PER_DAY = 10

# --- Technical Indicator Settings ---
# RSI (Relative Strength Index) settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# MACD (Moving Average Convergence Divergence) settings
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands settings
BB_PERIOD = 20
BB_STD = 2

# --- Logging Settings ---
# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = 'INFO'

# Save logs to files
LOG_TO_FILE = True

# Save trade history to CSV
LOG_TRADES_TO_CSV = True

# --- Backtesting Settings ---
# Date range for backtesting (ISO format: YYYY-MM-DD)
BACKTEST_START_DATE = '2024-01-01'
BACKTEST_END_DATE = '2024-12-31'

# Initial balance for backtesting simulation
BACKTEST_INITIAL_BALANCE = 10000