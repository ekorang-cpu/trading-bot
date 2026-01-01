# Python Predictive Trading Bot

This project is a trading bot that uses the `ccxt` library to automatically trade on multiple cryptocurrency exchanges. The core of the bot is a predictive model that analyzes market trends to forecast future price movements and execute trades.

## Key Features

- **Multi-Exchange Support**: Connects to over 100 exchanges via the `ccxt` library.
- **Automated Trading**: Executes buy and sell orders without manual intervention.
- **Predictive Strategy**: Implements a strategy to find trading opportunities.
- **Data Collection**: Fetches real-time and historical market data.

## Technology Stack

- **Language**: Python 3
- **Key Libraries**:
  - `ccxt`: For multi-exchange API interaction.
  - `pandas`: For data manipulation and analysis.

## How to Run

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy the example config: `cp config.example.py config.py`
4. Fill in your API keys and desired settings in `config.py`.
5. Run the bot: `python bot/main.py`

## ⚠️ Important Security Note

Never commit your `config.py` file with real API keys to the repository. The `.gitignore` file is configured to prevent this.