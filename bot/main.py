import time
import signal
import sys
from bot import exchange_interface
from bot import strategy
from bot import advanced_strategy
from bot.risk_manager import RiskManager
from bot.portfolio import Portfolio
from bot.logger import TradingLogger
import config


# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    print("\n\nShutdown signal received. Stopping bot gracefully...")
    shutdown_requested = True


def run_bot():
    """Main function to run the trading bot loop."""
    global shutdown_requested
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize logger
    logger = TradingLogger(config)
    
    # Log bot startup
    config_summary = {
        'Exchange': config.EXCHANGE_ID,
        'Symbol': config.SYMBOL,
        'Timeframe': config.TIMEFRAME,
        'Strategy': 'Advanced' if getattr(config, 'USE_ADVANCED_STRATEGY', False) else 'Simple',
        'Stop Loss': f"{getattr(config, 'STOP_LOSS_PERCENT', 2.0)}%",
        'Take Profit': f"{getattr(config, 'TAKE_PROFIT_PERCENT', 5.0)}%",
        'Position Size': f"{getattr(config, 'POSITION_SIZE_PERCENT', 10.0)}%",
        'Max Daily Trades': getattr(config, 'MAX_TRADES_PER_DAY', 10)
    }
    logger.log_bot_start(config_summary)
    
    # Initialize exchange
    exchange = exchange_interface.get_exchange()
    if not exchange:
        logger.error("Bot failed to start - could not connect to exchange")
        return
    
    logger.info(f"Successfully connected to {config.EXCHANGE_ID}")
    
    # Initialize risk manager and portfolio
    risk_manager = RiskManager(config)
    portfolio = Portfolio(exchange)
    
    # Determine which strategy to use
    use_advanced = getattr(config, 'USE_ADVANCED_STRATEGY', False)
    
    logger.info(f"Bot initialized successfully. Starting main loop...")
    print("\n" + "="*60)
    print("Trading Bot is running. Press Ctrl+C to stop.")
    print("="*60 + "\n")
    
    while not shutdown_requested:
        try:
            # 1. Fetch market data
            logger.debug(f"Fetching market data for {config.SYMBOL}...")
            ohlcv_data = exchange_interface.fetch_market_data(
                exchange=exchange,
                symbol=config.SYMBOL,
                timeframe=config.TIMEFRAME
            )
            
            if not ohlcv_data:
                logger.warning("No market data received, skipping this iteration")
                time.sleep(60)
                continue
            
            # 2. Analyze data and get a signal
            if use_advanced:
                signal_result, confidence, reason = advanced_strategy.analyze_data_advanced(
                    ohlcv_data, config
                )
            else:
                signal_result = strategy.analyze_data(ohlcv_data)
                confidence = 100 if signal_result != 'hold' else 0
                reason = "Simple moving average strategy"
            
            # Get current price
            current_price = ohlcv_data[-1][4]  # Close price
            
            # Log signal
            logger.log_signal(config.SYMBOL, signal_result, confidence, reason)
            
            # 3. Check for stop-loss and take-profit on existing positions
            if config.SYMBOL in risk_manager.open_positions:
                if risk_manager.check_stop_loss(config.SYMBOL, current_price):
                    logger.warning(f"Stop-loss triggered for {config.SYMBOL}")
                    signal_result = 'sell'
                    reason = "Stop-loss triggered"
                elif risk_manager.check_take_profit(config.SYMBOL, current_price):
                    logger.info(f"Take-profit triggered for {config.SYMBOL}")
                    signal_result = 'sell'
                    reason = "Take-profit triggered"
            
            # 4. Check risk limits before trading
            balance = portfolio.get_available_balance('USDT')
            can_trade, risk_reason = risk_manager.can_trade(balance)
            logger.log_risk_check(can_trade, risk_reason, risk_manager.get_risk_summary())
            
            # 5. Act on the signal
            if signal_result == 'buy' and can_trade and config.SYMBOL not in risk_manager.open_positions:
                logger.info("=== BUY SIGNAL - Placing order ===")
                
                # Calculate position size
                quantity = risk_manager.calculate_position_size(balance, current_price)
                
                # In production, uncomment this to place actual order:
                # try:
                #     order = exchange.create_market_buy_order(config.SYMBOL, quantity)
                #     logger.log_trade(
                #         config.SYMBOL, 'buy', current_price, quantity,
                #         order_id=order.get('id'), balance=balance
                #     )
                #     risk_manager.add_position(config.SYMBOL, current_price, quantity)
                #     portfolio.add_position(config.SYMBOL, 'buy', current_price, quantity)
                # except Exception as e:
                #     logger.error(f"Error placing buy order: {e}", exc_info=True)
                
                # For testing/demo mode:
                logger.info(f"[DEMO MODE] Would place BUY order:")
                logger.info(f"  Symbol: {config.SYMBOL}")
                logger.info(f"  Quantity: {quantity:.6f}")
                logger.info(f"  Price: ${current_price:.2f}")
                logger.info(f"  Value: ${quantity * current_price:.2f}")
                logger.log_trade(config.SYMBOL, 'buy', current_price, quantity, 
                               status='demo', balance=balance)
                
                # Track position (even in demo mode for testing)
                risk_manager.add_position(config.SYMBOL, current_price, quantity)
                portfolio.add_position(config.SYMBOL, 'buy', current_price, quantity)
                
            elif signal_result == 'sell' and config.SYMBOL in risk_manager.open_positions:
                logger.info("=== SELL SIGNAL - Placing order ===")
                
                position = risk_manager.open_positions[config.SYMBOL]
                quantity = position['quantity']
                
                # In production, uncomment this to place actual order:
                # try:
                #     order = exchange.create_market_sell_order(config.SYMBOL, quantity)
                #     pnl = portfolio.close_position(config.SYMBOL, current_price)
                #     logger.log_trade(
                #         config.SYMBOL, 'sell', current_price, quantity,
                #         order_id=order.get('id'), pnl=pnl, balance=balance
                #     )
                #     risk_manager.remove_position(config.SYMBOL)
                #     risk_manager.record_trade_result(pnl)
                # except Exception as e:
                #     logger.error(f"Error placing sell order: {e}", exc_info=True)
                
                # For testing/demo mode:
                entry_price = position['entry_price']
                pnl = (current_price - entry_price) * quantity
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                
                logger.info(f"[DEMO MODE] Would place SELL order:")
                logger.info(f"  Symbol: {config.SYMBOL}")
                logger.info(f"  Quantity: {quantity:.6f}")
                logger.info(f"  Entry Price: ${entry_price:.2f}")
                logger.info(f"  Exit Price: ${current_price:.2f}")
                logger.info(f"  P&L: ${pnl:.2f} ({pnl_percent:.2f}%)")
                logger.log_trade(config.SYMBOL, 'sell', current_price, quantity,
                               status='demo', pnl=pnl, balance=balance)
                
                # Close position (even in demo mode)
                portfolio.close_position(config.SYMBOL, current_price)
                risk_manager.remove_position(config.SYMBOL)
                risk_manager.record_trade_result(pnl)
                
            else:
                logger.info("=== HOLD - No action taken ===")
                if not can_trade:
                    logger.warning(f"Trading blocked: {risk_reason}")
            
            # 6. Log portfolio status
            current_prices = {config.SYMBOL: current_price}
            portfolio_summary = portfolio.get_portfolio_summary(current_prices)
            logger.log_portfolio_update(portfolio_summary)
            
            # Wait for the next interval
            logger.info(f"\nWaiting for next iteration...")
            
            # Sleep in smaller increments to check for shutdown
            sleep_duration = 3600  # 1 hour
            for _ in range(sleep_duration):
                if shutdown_requested:
                    break
                time.sleep(1)

        except KeyboardInterrupt:
            shutdown_requested = True
            break
        except Exception as e:
            logger.error(f"An error occurred in the main loop: {e}", exc_info=True)
            time.sleep(60)  # Wait a minute before retrying
    
    # Graceful shutdown
    logger.log_bot_stop("Graceful shutdown")
    logger.info("Exporting trade history...")
    portfolio.export_trade_history_csv()
    logger.info("Bot stopped successfully")
    print("\nBot stopped successfully. Goodbye!")


if __name__ == "__main__":
    run_bot()