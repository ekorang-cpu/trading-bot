"""
Advanced Trading Strategy Module

Multi-indicator strategy that combines:
- Moving averages for trend direction
- RSI for entry/exit timing
- MACD for confirmation
- Bollinger Bands for volatility assessment
"""

import pandas as pd
from bot import indicators


def analyze_advanced_strategy(df, config=None):
    """
    Analyze market data using multiple technical indicators.
    
    Generates signals only when multiple indicators align.
    
    :param df: DataFrame with OHLCV data and indicators
    :param config: Configuration object with strategy parameters
    :return: Signal ('buy', 'sell', or 'hold') and confidence score
    """
    if df is None or len(df) < 50:
        return 'hold', 0, "Insufficient data"
    
    # Get configuration parameters
    if config:
        rsi_oversold = getattr(config, 'RSI_OVERSOLD', 30)
        rsi_overbought = getattr(config, 'RSI_OVERBOUGHT', 70)
    else:
        rsi_oversold = 30
        rsi_overbought = 70
    
    # Ensure indicators are calculated
    if 'rsi' not in df.columns:
        df = indicators.add_all_indicators(df, config)
    
    # Get latest values
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    
    # Check for NaN values
    required_columns = ['rsi', 'macd', 'macd_signal', 'bb_upper', 'bb_lower', 
                       'ema_12', 'ema_26', 'close']
    if any(pd.isna(latest[col]) for col in required_columns):
        return 'hold', 0, "Waiting for indicator data"
    
    # Initialize scoring system
    buy_signals = 0
    sell_signals = 0
    max_signals = 5
    
    reasons = []
    
    # 1. RSI Analysis
    if latest['rsi'] < rsi_oversold:
        buy_signals += 1
        reasons.append(f"RSI oversold ({latest['rsi']:.2f})")
    elif latest['rsi'] > rsi_overbought:
        sell_signals += 1
        reasons.append(f"RSI overbought ({latest['rsi']:.2f})")
    
    # 2. MACD Analysis
    if latest['macd'] > latest['macd_signal'] and previous['macd'] <= previous['macd_signal']:
        buy_signals += 1
        reasons.append("MACD bullish crossover")
    elif latest['macd'] < latest['macd_signal'] and previous['macd'] >= previous['macd_signal']:
        sell_signals += 1
        reasons.append("MACD bearish crossover")
    
    # 3. EMA Trend Analysis
    if latest['ema_12'] > latest['ema_26']:
        buy_signals += 1
        reasons.append("Short-term EMA above long-term (bullish trend)")
    else:
        sell_signals += 1
        reasons.append("Short-term EMA below long-term (bearish trend)")
    
    # 4. Bollinger Bands Analysis
    if latest['close'] < latest['bb_lower']:
        buy_signals += 1
        reasons.append("Price below lower Bollinger Band (oversold)")
    elif latest['close'] > latest['bb_upper']:
        sell_signals += 1
        reasons.append("Price above upper Bollinger Band (overbought)")
    
    # 5. Price Momentum
    price_change = ((latest['close'] - previous['close']) / previous['close']) * 100
    if price_change > 1:
        buy_signals += 1
        reasons.append(f"Strong positive momentum ({price_change:.2f}%)")
    elif price_change < -1:
        sell_signals += 1
        reasons.append(f"Strong negative momentum ({price_change:.2f}%)")
    
    # Calculate confidence based on signal alignment
    buy_confidence = (buy_signals / max_signals) * 100
    sell_confidence = (sell_signals / max_signals) * 100
    
    # Generate signal based on confidence threshold
    min_confidence = 60  # Require at least 60% confidence (3 out of 5 indicators)
    
    if buy_confidence >= min_confidence and buy_confidence > sell_confidence:
        signal = 'buy'
        confidence = buy_confidence
        reason = f"BUY signal ({confidence:.0f}% confidence): " + ", ".join(reasons[:3])
    elif sell_confidence >= min_confidence and sell_confidence > buy_confidence:
        signal = 'sell'
        confidence = sell_confidence
        reason = f"SELL signal ({confidence:.0f}% confidence): " + ", ".join(reasons[:3])
    else:
        signal = 'hold'
        confidence = max(buy_confidence, sell_confidence)
        reason = f"HOLD (insufficient confidence: buy={buy_confidence:.0f}%, sell={sell_confidence:.0f}%)"
    
    return signal, confidence, reason


def get_strategy_state(df):
    """
    Get current state of all indicators for analysis.
    
    :param df: DataFrame with OHLCV data and indicators
    :return: Dictionary with current indicator values
    """
    if df is None or len(df) == 0:
        return {}
    
    latest = df.iloc[-1]
    
    return {
        'price': latest.get('close'),
        'rsi': latest.get('rsi'),
        'macd': latest.get('macd'),
        'macd_signal': latest.get('macd_signal'),
        'macd_histogram': latest.get('macd_histogram'),
        'bb_upper': latest.get('bb_upper'),
        'bb_middle': latest.get('bb_middle'),
        'bb_lower': latest.get('bb_lower'),
        'ema_12': latest.get('ema_12'),
        'ema_26': latest.get('ema_26'),
        'ema_50': latest.get('ema_50')
    }


def analyze_data_advanced(ohlcv, config=None):
    """
    Main entry point for advanced strategy analysis.
    Converts OHLCV data to DataFrame and runs advanced strategy.
    
    :param ohlcv: List of OHLCV data from exchange
    :param config: Configuration object
    :return: Tuple of (signal, confidence, reason)
    """
    if not ohlcv:
        return 'hold', 0, "No market data"
    
    # Convert to DataFrame
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Add all indicators
    df = indicators.add_all_indicators(df, config)
    
    # Run advanced strategy
    signal, confidence, reason = analyze_advanced_strategy(df, config)
    
    # Print analysis
    print(f"\n{'='*60}")
    print(f"Advanced Strategy Analysis")
    print(f"{'='*60}")
    print(f"Analyzing {len(df)} data points...")
    print(f"\nSignal: {signal.upper()} (Confidence: {confidence:.0f}%)")
    print(f"Reason: {reason}")
    
    # Print current indicator values
    state = get_strategy_state(df)
    print(f"\nCurrent Indicators:")
    print(f"  Price: ${state.get('price', 0):.2f}")
    print(f"  RSI: {state.get('rsi', 0):.2f}")
    print(f"  MACD: {state.get('macd', 0):.4f}")
    print(f"  MACD Signal: {state.get('macd_signal', 0):.4f}")
    print(f"  Bollinger Bands: ${state.get('bb_lower', 0):.2f} - ${state.get('bb_upper', 0):.2f}")
    print(f"  EMA(12): ${state.get('ema_12', 0):.2f}")
    print(f"  EMA(26): ${state.get('ema_26', 0):.2f}")
    print(f"{'='*60}\n")
    
    return signal, confidence, reason
