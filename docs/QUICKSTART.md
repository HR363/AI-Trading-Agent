# ⚡ Quick Start Guide

Get your AI Trading Agent running in 10 minutes!

## Step 1: Install Python Dependencies (2 min)

```bash
pip install -r requirements.txt
```

## Step 2: Get API Keys (5 min)

### Telegram API (Required)
1. Visit: https://my.telegram.org
2. Login → "API development tools"
3. Create app → Copy `api_id` and `api_hash`

### OpenAI API (Required)
1. Visit: https://platform.openai.com
2. Create API key
3. Copy the key (starts with `sk-...`)

### Trading Broker (Required - Choose One)

**Option A: Alpaca (Stocks) - Easier for beginners**
1. Visit: https://alpaca.markets
2. Sign up → Dashboard → Get API keys
3. Use paper trading URL: `https://paper-api.alpaca.markets`

**Option B: Binance (Crypto)**
1. Visit: https://binance.com
2. Account → API Management → Create API
3. For testing, use testnet: https://testnet.binance.vision

## Step 3: Configure (2 min)

Copy the example config:
```bash
copy .env.example .env
```

Edit `.env` file (use Notepad or VS Code):

```env
# REQUIRED - Telegram
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890
TELEGRAM_PHONE=+1234567890
TELEGRAM_CHANNEL_ID=@yourchannel

# REQUIRED - OpenAI
OPENAI_API_KEY=sk-proj-xxxxx

# REQUIRED - Broker (choose one)
TRADING_MODE=paper
BROKER=alpaca

# If using Alpaca:
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# If using Binance:
BINANCE_API_KEY=your_key
BINANCE_SECRET_KEY=your_secret
BINANCE_TESTNET=true
```

### Finding Your Telegram Channel ID

**For public channels:**
```
TELEGRAM_CHANNEL_ID=@channelname
```

**For private channels:**
1. Add @userinfobot to Telegram
2. Forward a message from the channel to the bot
3. Use the numeric ID it shows (e.g., `-1001234567890`)

## Step 4: Test Without Trading (1 min)

Test the signal parser first:
```bash
python test_parser.py
```

This will show you how the AI interprets different messages.

## Step 5: Dry Run (Monitor Only)

Watch your channel without executing trades:
```bash
python dry_run.py
```

This connects to Telegram and shows what trades WOULD be executed.

## Step 6: Paper Trading

Ready to test with paper trading?
```bash
python main.py
```

The agent will:
- ✅ Connect to Telegram
- ✅ Monitor your trading channel
- ✅ Parse signals with AI
- ✅ Execute trades (paper mode)

## Testing

Send a test message in your channel:
```
I entered BTCUSDT long at 45000, SL 44500, TP 46000
```

Watch the logs - you should see:
```
✅ Signal detected: ENTRY BTCUSDT BUY
💰 Position size: $100.00
✅ Position opened
```

## Common Issues

### ❌ "Could not access channel"
- Check channel ID is correct
- Make sure you're a member
- Use @ for public, numeric ID for private

### ❌ "Missing configuration"
- Check .env file exists
- Verify all required fields are filled
- No spaces around = signs

### ❌ "Failed to parse signal"
- OpenAI API key might be invalid
- Check you have credits on OpenAI account

### ❌ "Import Error"
- Run: `pip install -r requirements.txt`
- Make sure you're using Python 3.9+

## Next Steps

1. ✅ Test in dry-run mode for a few days
2. ✅ Verify the agent interprets signals correctly
3. ✅ When confident, switch to paper trading
4. ✅ Monitor paper trading for a week
5. ✅ Only then consider live trading

## Going Live (When Ready)

⚠️ **Only after thorough testing!**

1. Change in `.env`:
```env
TRADING_MODE=live
```

2. Update API endpoints:
```env
# Alpaca
ALPACA_BASE_URL=https://api.alpaca.markets

# Binance
BINANCE_TESTNET=false
```

3. **Start with tiny position sizes**:
```env
DEFAULT_POSITION_SIZE_PERCENT=0.5
MAX_POSITION_SIZE_PERCENT=1
```

4. Monitor closely!

## Stopping the Agent

Press `Ctrl+C` to stop safely.

## File Structure

```
TRADING-AGENT/
├── main.py              # Run for paper/live trading
├── dry_run.py          # Run to monitor without trading
├── test_parser.py      # Test signal parsing
├── .env                # Your configuration (create this!)
├── requirements.txt    # Dependencies
└── setup.md           # Detailed setup guide
```

## Support

- 📖 Full guide: Read `setup.md`
- 🔍 Check logs: `logs/` directory
- 🧪 Test parsing: `python test_parser.py`
- 👀 Dry run: `python dry_run.py`

## Risk Reminder

⚠️ Automated trading carries significant risk:
- Start in paper mode
- Test thoroughly
- Use small sizes
- Monitor regularly
- Understand the risks

---

**You're ready to go! Start with `python test_parser.py` 🚀**
