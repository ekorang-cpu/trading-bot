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

# Amount of the base currency to use for each trade.
TRADE_AMOUNT = 100  # Example: a value in USDT for a 'BTC/USDT' pair.