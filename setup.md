# AI Trading Agent - Setup Guide

## Overview
This trading agent monitors your Telegram trading community and automatically executes trades based on signals from the community owner.

## Prerequisites

1. **Python 3.9+** installed
2. **Telegram Account** with access to the trading channel
3. **Trading Account** (Alpaca for stocks or Binance for crypto)
4. **OpenAI API Key** for AI signal parsing

## Step-by-Step Setup

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Click on "API development tools"
4. Create a new application
5. Copy your `api_id` and `api_hash`

### 2. Get Your Telegram Channel ID

Option A: Using a bot
1. Add @userinfobot to your Telegram
2. Forward a message from the trading channel to the bot
3. It will show you the channel ID

Option B: Using the channel username
- If the channel is public, you can use `@channelname`
- If private, you'll need the numeric ID (starts with -100)

### 3. Setup Trading Broker

#### For Stocks (Alpaca):
1. Go to https://alpaca.markets
2. Sign up for an account
3. Get your API keys from the dashboard
4. Start with paper trading: https://paper-api.alpaca.markets

#### For Crypto (Binance):
1. Go to https://binance.com
2. Create an account
3. Go to API Management
4. Create a new API key
5. Save your API Key and Secret Key
6. For testing, use Binance Testnet: https://testnet.binance.vision

### 4. Get OpenAI API Key

1. Go to https://platform.openai.com
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy and save it securely

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment

1. Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

2. Open `.env` and fill in your credentials:

```env
# Telegram
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
TELEGRAM_CHANNEL_ID=@yourchannel or -1001234567890

# OpenAI
OPENAI_API_KEY=sk-...

# Trading
TRADING_MODE=paper
BROKER=alpaca

# Alpaca (if using)
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# OR Binance (if using)
BINANCE_API_KEY=...
BINANCE_SECRET_KEY=...
BINANCE_TESTNET=true

# Risk Management
DEFAULT_POSITION_SIZE_PERCENT=2
MAX_POSITION_SIZE_PERCENT=5
MAX_OPEN_POSITIONS=5
MAX_DAILY_LOSS_PERCENT=5
```

### 7. First Run (Paper Trading)

Always start in paper trading mode to test:

```bash
python main.py
```

The agent will:
1. Connect to Telegram
2. Start monitoring the trading channel
3. Parse messages using AI
4. Execute trades automatically (paper mode)

### 8. Test the Agent

Send a test message in your trading channel like:
- "I entered BTCUSDT long at 45000"
- "Taking 50% partial"
- "Moving SL to breakeven"

Watch the logs to see how the agent interprets and acts on messages.

### 9. Go Live (When Ready)

⚠️ **IMPORTANT**: Only switch to live trading after thorough testing!

1. Change in `.env`:
```env
TRADING_MODE=live
```

2. Update to live API endpoints:
- Alpaca: `https://api.alpaca.markets`
- Binance: Set `BINANCE_TESTNET=false`

3. Start with small position sizes
4. Monitor closely for the first few days

## Understanding the Logs

The agent logs everything to both console and `logs/` directory:

- 🟢 `INFO` - General information
- 🟡 `WARNING` - Something to be aware of
- 🔴 `ERROR` - Something went wrong
- 🟢 `SUCCESS` - Trade executed successfully

## Risk Management

The agent includes several safety features:

1. **Position Sizing**: Default 2% per trade
2. **Max Positions**: Limit simultaneous open positions
3. **Daily Loss Limit**: Stop trading if daily loss exceeds threshold
4. **Confidence Threshold**: Only trade high-confidence signals (>70%)

## Troubleshooting

### "Could not access channel"
- Verify the channel ID is correct
- Make sure you're a member of the channel
- For private channels, use numeric ID

### "Failed to parse signal"
- Check OpenAI API key is valid
- Message might not be a trading signal
- Check logs for details

### "Trade execution failed"
- Verify broker API credentials
- Check account has sufficient balance
- Ensure symbol format is correct (BTCUSDT for Binance, BTC/USD for Alpaca)

### Telegram Authentication
First run will ask for phone verification:
1. Enter your phone number with country code
2. Check Telegram for verification code
3. Enter the code
4. Session will be saved for future runs

## Customization

### Adjust Risk Parameters

In `.env`, modify:
```env
DEFAULT_POSITION_SIZE_PERCENT=1  # More conservative
MAX_OPEN_POSITIONS=3             # Fewer positions
MAX_DAILY_LOSS_PERCENT=3         # Tighter loss limit
```

### Change AI Model

For faster/cheaper parsing:
```env
OPENAI_MODEL=gpt-3.5-turbo
```

For better accuracy:
```env
OPENAI_MODEL=gpt-4-turbo-preview
```

### Add More Brokers

Edit `broker_interface.py` to add support for other brokers like:
- Interactive Brokers
- TD Ameritrade
- Kraken
- FTX

## Monitoring

### Portfolio Status
The agent logs portfolio status after each trade:
- Current balance
- Open positions
- Daily PnL
- Unrealized PnL

### Manual Check
You can also check your broker's dashboard for real-time positions.

## Best Practices

1. **Always test in paper mode first**
2. **Start with small position sizes**
3. **Monitor the first week closely**
4. **Review trade history regularly**
5. **Keep API keys secure**
6. **Use 2FA on all accounts**
7. **Set up alerts for large losses**
8. **Have a kill switch ready (Ctrl+C)**

## Support & Community

For issues or questions:
1. Check the logs in `logs/` directory
2. Review this setup guide
3. Check broker API documentation
4. Test with simple signals first

## License & Disclaimer

This is educational software. Use at your own risk. Always:
- Test thoroughly before live trading
- Start with small amounts
- Understand the risks of automated trading
- Keep control of your accounts
- Monitor the agent regularly

**Past performance does not guarantee future results.**

Happy Trading! 🚀📈
