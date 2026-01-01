import time
from bot import exchange_interface
from bot import strategy
import config

def run_bot():
    """Main function to run the trading bot loop."""
    print("Starting trading bot...")
    exchange = exchange_interface.get_exchange()

    if not exchange:
        print("Bot failed to start. Exiting.")
        return

    print(f"Successfully connected to {config.EXCHANGE_ID}.")
    print(f"Trading symbol: {config.SYMBOL}")
    print(f"Data timeframe: {config.TIMEFRAME}")

    while True:
        try:
            # 1. Fetch market data
            ohlcv_data = exchange_interface.fetch_market_data(
                exchange=exchange,
                symbol=config.SYMBOL,
                timeframe=config.TIMEFRAME
            )

            # 2. Analyze data and get a signal
            signal = strategy.analyze_data(ohlcv_data)

            # 3. Act on the signal (buy, sell, hold)
            if signal == 'buy':
                print("--- ACTION: Placing BUY order. ---")
                # TODO: Implement buy order logic
                # exchange.create_market_buy_order(config.SYMBOL, config.TRADE_AMOUNT)
            elif signal == 'sell':
                print("--- ACTION: Placing SELL order. ---")
                # TODO: Implement sell order logic
                # exchange.create_market_sell_order(config.SYMBOL, config.TRADE_AMOUNT)
            else:
                print("--- ACTION: Holding position. ---")

            # Wait for the next interval
            print("\nWaiting for the next candle...")
            time.sleep(3600)  # Wait for 1 hour (adjust as needed for your timeframe)

        except Exception as e:
            print(f"An error occurred in the main loop: {e}")
            time.sleep(60) # Wait a minute before retrying

if __name__ == "__main__":
    run_bot()