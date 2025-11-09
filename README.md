# 🤖 AI Trading Agent# 🤖 AI Trading Agent



An intelligent trading bot that monitors your Telegram trading community and automatically executes trades based on signals.An intelligent trading bot that monitors your Telegram trading community and automatically executes trades based on signals from the group owner.



## 🚀 Quick Start## 🎯 Problem It Solves



```powershellAs a busy, hardworking person, you can't always monitor your trading community or execute trades on time. This agent:

# 1. Install dependencies

pip install -r requirements.txt- ✅ Monitors your Telegram trading channel 24/7

- ✅ Understands natural language trading signals using AI

# 2. Find your Telegram channel ID- ✅ Automatically executes entries, partials, and stop-loss moves

python scripts/find_channel_id.py- ✅ Manages risk with position sizing and daily loss limits

- ✅ Never misses a trade opportunity

# 3. Configure .env file

# Edit .env with your credentials## 🚀 Features



# 4. Start trading### Signal Detection

python main.py- **Entry Signals**: "I entered BTCUSDT long at 45000"

```- **Entry Alerts**: "Getting ready to enter around 45000-45200"

- **Partial Exits**: "Took 50% off at 46000"

## 📁 Project Structure- **Stop-Loss Moves**: "Moving SL to breakeven"

- **Position Closes**: "Closed the position"

```

TRADING-AGENT/### AI-Powered Parsing

├── main.py                 # Main entry pointUses GPT-4 to understand informal trading messages and extract:

├── requirements.txt        # Python dependencies- Symbol (BTC, ETH, AAPL, TSLA, etc.)

├── .env                    # Your configuration (don't commit!)- Direction (long/short)

│- Entry price or zone

├── brokers/               # Broker integrations- Stop-loss levels

│   ├── broker_interface.py- Take-profit targets

│   ├── mt5_broker.py- Partial percentages

│   ├── alpaca_broker.py

│   └── binance_broker.py### Risk Management

│- Position sizing (default 2% per trade)

├── config/                # Configuration files- Maximum simultaneous positions (default 5)

│   ├── config.py- Daily loss limits (default 5%)

│   ├── models.py- Confidence thresholds (minimum 70%)

│   ├── .env.example

│   └── .gitignore### Multi-Broker Support

│- **Alpaca**: Stocks and forex trading

├── utils/                 # Core utilities- **Binance**: Cryptocurrency trading

│   ├── signal_parser.py- Easy to extend for other brokers

│   ├── position_manager.py

│   └── telegram_monitor.py## 📁 Project Structure

│

├── scripts/               # Helper scripts```

│   ├── find_channel_id.pyTRADING-AGENT/

│   ├── test_parser.py├── main.py                 # Entry point

│   ├── dashboard.py├── config.py               # Configuration management

│   ├── dry_run.py├── models.py               # Data models

│   ├── launcher.bat├── signal_parser.py        # AI signal parsing

│   └── setup_mt5.bat├── broker_interface.py     # Broker integrations

│├── position_manager.py     # Trade execution & risk management

├── docs/                  # Documentation├── telegram_monitor.py     # Telegram channel monitoring

│   ├── README.md          # Full documentation├── requirements.txt        # Dependencies

│   ├── QUICKSTART.md      # Quick setup guide├── .env.example           # Configuration template

│   ├── MT5_SETUP.md       # MT5 specific setup├── .gitignore             # Git ignore file

│   ├── YOUR_SETUP.md      # Your custom setup└── setup.md               # Detailed setup guide

│   └── TROUBLESHOOTING.md # Common issues```

│

└── logs/                  # Log files## 🛠️ Quick Start

```

### 1. Install Dependencies

## ✨ Features

```bash

- 📱 **Telegram Monitoring** - Monitor trading channels 24/7pip install -r requirements.txt

- 🤖 **AI Signal Parsing** - GPT-4 powered message understanding```

- 💰 **Multi-Broker Support** - MT5 (IC Markets), Alpaca, Binance

- 🛡️ **Risk Management** - Position sizing, loss limits, max positions### 2. Configure

- 📊 **Portfolio Tracking** - Real-time P&L and position monitoring

```bash

## 📖 Documentationcopy .env.example .env

```

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in 10 minutes

- **[MT5 Setup Guide](docs/MT5_SETUP.md)** - Complete MT5/IC Markets setupEdit `.env` with your credentials:

- **[Your Setup Guide](docs/YOUR_SETUP.md)** - Customized for your configuration- Telegram API credentials

- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues & solutions- OpenAI API key

- **[Full Documentation](docs/README.md)** - Complete project documentation- Broker API keys (Alpaca or Binance)



## 🔧 Configuration### 3. Run (Paper Trading)



Edit `.env` file:```bash

python main.py

```env```

# Telegram

TELEGRAM_CHANNEL_ID=your_channel_id### 4. Test

TELEGRAM_API_ID=your_api_id

TELEGRAM_API_HASH=your_api_hashSend a test signal in your Telegram channel:

TELEGRAM_PHONE=your_phone```

I entered BTCUSDT long at 45000, SL 44500, TP 46000, 47000

# OpenAI```

OPENAI_API_KEY=your_openai_key

Watch the agent parse and execute the trade!

# Broker (choose one)

BROKER=mt5## 📖 Full Setup Guide

MT5_ACCOUNT=your_account

MT5_PASSWORD=your_passwordSee [setup.md](setup.md) for detailed instructions on:

MT5_SERVER=ICMarkets-Demo- Getting Telegram API credentials

```- Finding your channel ID

- Setting up Alpaca or Binance accounts

## 🎯 Supported Brokers- Configuring risk parameters

- Testing and going live

- **MT5** - Forex, indices, commodities (IC Markets, etc.)

- **Alpaca** - US stocks, ETFs## 🔒 Safety Features

- **Binance** - Cryptocurrency

1. **Paper Trading Mode**: Test without risking real money

## ⚡ Quick Commands2. **Confidence Filtering**: Only trades high-confidence signals

3. **Position Limits**: Prevents over-exposure

```powershell4. **Daily Loss Limits**: Stops trading after threshold

# Find Telegram channel ID5. **Comprehensive Logging**: Track every action

python scripts/find_channel_id.py

## 📊 Example Usage

# Test signal parsing

python scripts/test_parser.pyThe agent understands various signal formats:



# View portfolio status```

python scripts/dashboard.py✅ "Just entered BTC long at 45,000"

✅ "Taking position on AAPL at 180.50, stop at 178"

# Monitor without trading✅ "Getting ready for ETH entry around 2500-2520"

python scripts/dry_run.py✅ "Took 50% partial on my BTC position"

✅ "Moving stop loss to breakeven on TSLA"

# Start trading✅ "Closed my position on AAPL"

python main.py```

```

## ⚙️ Configuration

## 🛡️ Safety Features

Key settings in `.env`:

- ✅ Paper trading mode

- ✅ Position size limits (2-5%)```env

- ✅ Maximum open positions (5)# Trading Mode

- ✅ Daily loss limits (5%)TRADING_MODE=paper          # paper or live

- ✅ Confidence filtering (≥70%)

# Broker

## ⚠️ Risk WarningBROKER=alpaca               # alpaca or binance



**Important**: Automated trading involves significant risk. Always:# Risk Management

- Start with demo/paper tradingDEFAULT_POSITION_SIZE_PERCENT=2

- Test thoroughly (2+ weeks minimum)MAX_POSITION_SIZE_PERCENT=5

- Use proper position sizingMAX_OPEN_POSITIONS=5

- Never risk more than you can afford to loseMAX_DAILY_LOSS_PERCENT=5

- Monitor regularly```



## 📝 License## 📈 Monitoring



MIT License - Use at your own riskThe agent provides real-time updates:



## 🙏 Support```

✅ Signal detected: ENTRY BTCUSDT BUY

For setup help and troubleshooting:💰 Position size: $100.00

- Read [docs/YOUR_SETUP.md](docs/YOUR_SETUP.md) for step-by-step instructions✅ Position opened: BTCUSDT @ 45000

- Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues📊 Portfolio - Balance: $5000.00, Open: 1, Daily PnL: $0.00

- Review [docs/MT5_SETUP.md](docs/MT5_SETUP.md) for MT5-specific setup```



---## 🛡️ Risk Disclaimer



**Ready to start?** → Read [docs/YOUR_SETUP.md](docs/YOUR_SETUP.md) 🚀**Important**: This is educational software. Automated trading involves significant risk. Always:

- Test thoroughly in paper mode
- Start with small position sizes
- Monitor the agent regularly
- Understand the risks
- Keep control of your accounts

## 🔧 Extending

### Add More Brokers

Edit `broker_interface.py` to add support for:
- Interactive Brokers
- TD Ameritrade
- Kraken
- Any broker with a Python API

### Customize Signal Parsing

Modify the prompt in `signal_parser.py` to:
- Handle specific message formats
- Extract additional information
- Support different languages

### Add Features

Potential enhancements:
- Trade history database
- Performance analytics
- Telegram notifications back to you
- Web dashboard
- Backtesting mode

## 📝 License

MIT License - Use at your own risk

## 🙏 Acknowledgments

Built for students and busy traders who want to automate their trading based on trusted community signals.

---

**Happy Trading! 🚀📈**

*Remember: Past performance doesn't guarantee future results. Trade responsibly!*

