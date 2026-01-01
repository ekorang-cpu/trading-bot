"""
Advanced Technical Indicators Module

This module implements various technical indicators used for trading analysis:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- EMA (Exponential Moving Average)
"""

import pandas as pd
import numpy as np


def calculate_rsi(prices, period=14):
    """
    Calculate the Relative Strength Index (RSI).
    
    RSI measures the magnitude of recent price changes to evaluate
    overbought or oversold conditions.
    
    :param prices: Series or array of closing prices
    :param period: Number of periods for RSI calculation (default: 14)
    :return: Series of RSI values (0-100)
    """
    if isinstance(prices, list):
        prices = pd.Series(prices)
    
    # Calculate price changes
    delta = prices.diff()
    
    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    # Calculate RS and RSI
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_ema(prices, period):
    """
    Calculate the Exponential Moving Average (EMA).
    
    EMA gives more weight to recent prices compared to simple moving average.
    
    :param prices: Series or array of prices
    :param period: Number of periods for EMA calculation
    :return: Series of EMA values
    """
    if isinstance(prices, list):
        prices = pd.Series(prices)
    
    return prices.ewm(span=period, adjust=False).mean()


def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate the MACD (Moving Average Convergence Divergence).
    
    MACD is a trend-following momentum indicator that shows the relationship
    between two moving averages of prices.
    
    :param prices: Series or array of closing prices
    :param fast_period: Period for fast EMA (default: 12)
    :param slow_period: Period for slow EMA (default: 26)
    :param signal_period: Period for signal line (default: 9)
    :return: Dictionary with 'macd', 'signal', and 'histogram'
    """
    if isinstance(prices, list):
        prices = pd.Series(prices)
    
    # Calculate EMAs
    ema_fast = calculate_ema(prices, fast_period)
    ema_slow = calculate_ema(prices, slow_period)
    
    # Calculate MACD line
    macd_line = ema_fast - ema_slow
    
    # Calculate signal line
    signal_line = calculate_ema(macd_line, signal_period)
    
    # Calculate histogram
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """
    Calculate Bollinger Bands.
    
    Bollinger Bands consist of a middle band (SMA) and two outer bands
    that are standard deviations away from the middle band.
    
    :param prices: Series or array of closing prices
    :param period: Number of periods for moving average (default: 20)
    :param std_dev: Number of standard deviations for bands (default: 2)
    :return: Dictionary with 'upper', 'middle', and 'lower' bands
    """
    if isinstance(prices, list):
        prices = pd.Series(prices)
    
    # Calculate middle band (SMA)
    middle_band = prices.rolling(window=period).mean()
    
    # Calculate standard deviation
    std = prices.rolling(window=period).std()
    
    # Calculate upper and lower bands
    upper_band = middle_band + (std_dev * std)
    lower_band = middle_band - (std_dev * std)
    
    return {
        'upper': upper_band,
        'middle': middle_band,
        'lower': lower_band
    }


def calculate_sma(prices, period):
    """
    Calculate Simple Moving Average (SMA).
    
    :param prices: Series or array of prices
    :param period: Number of periods for SMA calculation
    :return: Series of SMA values
    """
    if isinstance(prices, list):
        prices = pd.Series(prices)
    
    return prices.rolling(window=period).mean()


def add_all_indicators(df, config=None):
    """
    Add all technical indicators to a dataframe.
    
    :param df: DataFrame with OHLCV data (must have 'close' column)
    :param config: Configuration object with indicator parameters (optional)
    :return: DataFrame with all indicators added
    """
    if config is None:
        # Default parameters
        rsi_period = 14
        macd_fast = 12
        macd_slow = 26
        macd_signal = 9
        bb_period = 20
        bb_std = 2
    else:
        # Use config parameters
        rsi_period = getattr(config, 'RSI_PERIOD', 14)
        macd_fast = getattr(config, 'MACD_FAST', 12)
        macd_slow = getattr(config, 'MACD_SLOW', 26)
        macd_signal = getattr(config, 'MACD_SIGNAL', 9)
        bb_period = getattr(config, 'BB_PERIOD', 20)
        bb_std = getattr(config, 'BB_STD', 2)
    
    # Calculate RSI
    df['rsi'] = calculate_rsi(df['close'], period=rsi_period)
    
    # Calculate MACD
    macd = calculate_macd(df['close'], macd_fast, macd_slow, macd_signal)
    df['macd'] = macd['macd']
    df['macd_signal'] = macd['signal']
    df['macd_histogram'] = macd['histogram']
    
    # Calculate Bollinger Bands
    bb = calculate_bollinger_bands(df['close'], period=bb_period, std_dev=bb_std)
    df['bb_upper'] = bb['upper']
    df['bb_middle'] = bb['middle']
    df['bb_lower'] = bb['lower']
    
    # Calculate EMAs
    df['ema_12'] = calculate_ema(df['close'], 12)
    df['ema_26'] = calculate_ema(df['close'], 26)
    df['ema_50'] = calculate_ema(df['close'], 50)
    
    # Calculate SMAs (for compatibility with existing strategy)
    df['sma_5'] = calculate_sma(df['close'], 5)
    df['sma_20'] = calculate_sma(df['close'], 20)
    
    return df
