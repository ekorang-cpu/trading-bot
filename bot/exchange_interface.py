import ccxt
import config

def get_exchange():
    """
    Initializes and returns the exchange instance using settings from config.
    """
    try:
        exchange_class = getattr(ccxt, config.EXCHANGE_ID)
        exchange = exchange_class({
            'apiKey': config.API_KEY,
            'secret': config.SECRET_KEY,
            'options': {
                'defaultType': 'spot',
            },
        })
        # Optional: Set sandbox mode if the exchange supports it
        # exchange.set_sandbox_mode(True)
        return exchange
    except AttributeError:
        print(f"Error: The exchange '{config.EXCHANGE_ID}' is not supported by ccxt.")
        return None
    except Exception as e:
        print(f"Error connecting to the exchange: {e}")
        return None

def fetch_market_data(exchange, symbol, timeframe):
    """
    Fetches historical market data (OHLCV) for a given symbol and timeframe.
    """
    try:
        print(f"Fetching market data for {symbol} on timeframe {timeframe}...")
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
        return ohlcv
    except ccxt.BaseError as e:
        print(f"Error fetching market data: {e}")
        return None