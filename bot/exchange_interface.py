import ccxt
import config

_PLACEHOLDER_API_KEY = 'YOUR_API_KEY_HERE'
_PLACEHOLDER_SECRET_KEY = 'YOUR_SECRET_KEY_HERE'


def _validate_credentials():
    """
    Validates that API credentials have been properly configured.
    Returns (is_valid, error_message).
    """
    api_key = getattr(config, 'API_KEY', '')
    secret_key = getattr(config, 'SECRET_KEY', '')

    if not api_key or not secret_key:
        return False, "API credentials are missing. Please set API_KEY and SECRET_KEY in config.py."

    if api_key == _PLACEHOLDER_API_KEY or secret_key == _PLACEHOLDER_SECRET_KEY:
        return False, (
            "API credentials are still set to placeholder values. "
            "Please replace 'YOUR_API_KEY_HERE' and 'YOUR_SECRET_KEY_HERE' "
            "in config.py with your actual exchange API credentials."
        )

    return True, None


def get_exchange():
    """
    Initializes, authenticates, and returns the exchange instance.

    Performs credential validation and a live connection test so that
    configuration problems are caught at startup rather than during trading.
    Returns None on any failure.
    """
    # Step 1: Validate credentials before attempting to connect.
    valid, error_message = _validate_credentials()
    if not valid:
        print(f"Login error: {error_message}")
        return None

    # Step 2: Build the exchange object.
    try:
        exchange_class = getattr(ccxt, config.EXCHANGE_ID)
    except AttributeError:
        print(f"Login error: The exchange '{config.EXCHANGE_ID}' is not supported by ccxt.")
        return None

    try:
        exchange = exchange_class({
            'apiKey': config.API_KEY,
            'secret': config.SECRET_KEY,
            'options': {
                'defaultType': 'spot',
            },
        })
        # Optional: Set sandbox mode if the exchange supports it.
        # exchange.set_sandbox_mode(True)
    except Exception as e:
        print(f"Login error: Failed to initialize exchange '{config.EXCHANGE_ID}': {e}")
        return None

    # Step 3: Test the connection by loading markets. This is a lightweight call
    # that also verifies network connectivity and, for authenticated endpoints,
    # confirms the API key is accepted.
    try:
        exchange.load_markets()
    except ccxt.AuthenticationError as e:
        print(
            f"Login error: Authentication failed for exchange '{config.EXCHANGE_ID}'. "
            f"Please check that your API_KEY and SECRET_KEY are correct and have the "
            f"necessary permissions. Details: {e}"
        )
        return None
    except ccxt.NetworkError as e:
        print(
            f"Login error: Could not reach exchange '{config.EXCHANGE_ID}'. "
            f"Please check your internet connection. Details: {e}"
        )
        return None
    except ccxt.ExchangeError as e:
        print(f"Login error: Exchange '{config.EXCHANGE_ID}' returned an error: {e}")
        return None
    except Exception as e:
        print(f"Login error: Unexpected error while connecting to '{config.EXCHANGE_ID}': {e}")
        return None

    print(f"Successfully logged in to {config.EXCHANGE_ID}.")
    return exchange


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