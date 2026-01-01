import pandas as pd

def analyze_data(ohlcv):
    """
    Analyzes market data to generate a trading signal.
    This is a placeholder for your predictive logic.
    
    :param ohlcv: A list of lists containing OHLCV data.
    :return: A string signal: 'buy', 'sell', or 'hold'.
    """
    if not ohlcv:
        return 'hold'

    # Convert to a pandas DataFrame for easier analysis
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    print(f"Analyzing {len(df)} data points...")

    # --- Simple Example Strategy: Moving Average Crossover ---
    # 1. Calculate a short-term moving average (e.g., 5 periods)
    df['short_ma'] = df['close'].rolling(window=5).mean()
    # 2. Calculate a long-term moving average (e.g., 20 periods)
    df['long_ma'] = df['close'].rolling(window=20).mean()

    # Avoid acting on incomplete data
    if df.isnull().values.any():
        print("Waiting for more data to generate moving averages...")
        return 'hold'

    # 3. Generate a signal
    latest_short_ma = df['short_ma'].iloc[-1]
    latest_long_ma = df['long_ma'].iloc[-1]
    
    print(f"Latest Short MA: {latest_short_ma:.2f}, Latest Long MA: {latest_long_ma:.2f}")

    if latest_short_ma > latest_long_ma:
        print("Signal: BUY (Short-term MA crossed above long-term MA)")
        return 'buy'
    elif latest_short_ma < latest_long_ma:
        print("Signal: SELL (Short-term MA crossed below long-term MA)")
        return 'sell'
    else:
        print("Signal: HOLD")
        return 'hold'