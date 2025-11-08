# 🔧 Troubleshooting Guide

Common issues and solutions for the AI Trading Agent.

## Installation Issues

### "Module not found" errors

**Problem**: Import errors when running the agent

**Solution**:
```bash
pip install -r requirements.txt
```

If still failing:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Python version issues

**Problem**: Code doesn't run or syntax errors

**Solution**: You need Python 3.9 or higher
```bash
python --version
```

If too old, download from: https://www.python.org/downloads/

## Telegram Connection Issues

### "Could not access channel"

**Problem**: Agent can't connect to your Telegram channel

**Solutions**:

1. **Check Channel ID format**:
   - Public channel: `@channelname`
   - Private channel: `-1001234567890` (numeric ID)

2. **Get the correct channel ID**:
   - Add @userinfobot to Telegram
   - Forward a message from the channel to the bot
   - Use the ID it shows

3. **Verify you're a member**:
   - Make sure you can see messages in the channel
   - If private, you must be added as a member

### "Authentication failed"

**Problem**: Can't authenticate with Telegram

**Solutions**:

1. **Check credentials**:
   ```env
   TELEGRAM_API_ID=12345678  # Just numbers
   TELEGRAM_API_HASH=abc123  # No quotes
   TELEGRAM_PHONE=+1234567890  # Include country code
   ```

2. **Delete session file and retry**:
   ```bash
   del trading_agent_session.session
   python main.py
   ```

3. **Verify at https://my.telegram.org**:
   - Check your API credentials are active
   - App not suspended

### "Phone code required"

**Problem**: First run asks for verification code

**Solution**: This is normal!
1. Check your Telegram app for a code
2. Enter the code when prompted
3. Session will be saved for future runs

## OpenAI API Issues

### "Invalid API key"

**Problem**: OpenAI authentication fails

**Solutions**:

1. **Check API key format**:
   ```env
   OPENAI_API_KEY=sk-proj-...  # Should start with sk-
   ```

2. **Verify on OpenAI dashboard**:
   - Go to https://platform.openai.com/api-keys
   - Check key is active
   - Create a new one if needed

3. **Check billing**:
   - Go to https://platform.openai.com/account/billing
   - Add payment method if needed
   - Ensure you have credits

### "Rate limit exceeded"

**Problem**: Too many requests to OpenAI

**Solution**: 
- Wait a minute and retry
- Consider upgrading OpenAI plan
- Reduce message volume during testing

### "Failed to parse signal"

**Problem**: AI can't understand the message

**Solutions**:

1. **Check message format**:
   - Test with `python test_parser.py`
   - Try simpler messages
   - Ensure messages contain trading info

2. **Improve prompt** (advanced):
   - Edit `signal_parser.py`
   - Add examples specific to your channel's format

## Broker Connection Issues

### Alpaca Issues

**Problem**: Can't connect to Alpaca

**Solutions**:

1. **Check credentials**:
   ```env
   ALPACA_API_KEY=PK...
   ALPACA_SECRET_KEY=...
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   ```

2. **Verify keys at dashboard**:
   - Go to https://app.alpaca.markets
   - Check API keys are active
   - Regenerate if needed

3. **Check market hours**:
   - Alpaca for stocks only works during market hours (testing)
   - Try during market hours: Mon-Fri 9:30-16:00 EST

### Binance Issues

**Problem**: Can't connect to Binance

**Solutions**:

1. **Check credentials**:
   ```env
   BINANCE_API_KEY=...
   BINANCE_SECRET_KEY=...
   BINANCE_TESTNET=true  # For testing
   ```

2. **Verify API permissions**:
   - Go to Binance account → API Management
   - Enable "Spot & Margin Trading"
   - Check IP whitelist (if enabled)

3. **Test with testnet first**:
   - Use https://testnet.binance.vision
   - Get testnet API keys
   - Set `BINANCE_TESTNET=true`

### "Symbol not found"

**Problem**: Can't find trading symbol

**Solutions**:

1. **Check symbol format**:
   - Binance: `BTCUSDT`, `ETHUSDT` (no separator)
   - Alpaca: `BTC/USD`, `AAPL`, `TSLA`

2. **Verify symbol exists**:
   - Check on broker's website
   - Try `python dashboard.py` to test prices

## Trading Execution Issues

### "Position size too small"

**Problem**: Can't open position with available funds

**Solutions**:

1. **Check account balance**:
   ```bash
   python dashboard.py
   ```

2. **Increase position size**:
   ```env
   DEFAULT_POSITION_SIZE_PERCENT=5  # Use more per trade
   ```

3. **Fund account** (for paper trading):
   - Alpaca paper: Already funded ($100k default)
   - Binance testnet: Get test funds from faucet

### "Max positions reached"

**Problem**: Can't open new positions

**Solutions**:

1. **Close existing positions**:
   - Wait for signals to close
   - Manually close on broker platform

2. **Increase limit**:
   ```env
   MAX_OPEN_POSITIONS=10
   ```

### "Daily loss limit reached"

**Problem**: Agent stops trading after losses

**Solutions**:

1. **This is a safety feature!** Review why:
   - Check trade history
   - Review signals being executed
   - Consider if settings need adjustment

2. **Adjust limit** (carefully!):
   ```env
   MAX_DAILY_LOSS_PERCENT=10  # Higher limit
   ```

3. **Wait for next day**:
   - Limit resets every 24 hours
   - Use this time to review performance

## Signal Parsing Issues

### Signals not being executed

**Problem**: Messages detected but no trades

**Possible reasons**:

1. **Confidence too low**:
   - Agent requires ≥70% confidence
   - Test with: `python test_parser.py`
   - Message might be ambiguous

2. **Missing information**:
   - Entry signals need: symbol, side, entry price
   - Check logs for details

3. **Risk limits**:
   - Check `python dashboard.py`
   - May have hit max positions or daily loss

4. **Not an entry signal**:
   - "Getting ready" = entry alert (doesn't execute)
   - "Entered" = entry signal (executes)

### Wrong symbol extracted

**Problem**: AI extracts wrong trading symbol

**Solutions**:

1. **Use clear symbol names**:
   - Good: "BTCUSDT", "BTC", "AAPL"
   - Bad: "Bitcoin", "that coin we discussed"

2. **Test parsing**:
   ```bash
   python test_parser.py
   ```

3. **Improve prompt** (advanced):
   - Edit system_prompt in `signal_parser.py`
   - Add your channel's specific symbol formats

## File and Permission Issues

### "Permission denied" writing logs

**Problem**: Can't write to logs directory

**Solution**:
```bash
mkdir logs
# Or on Windows:
md logs
```

### ".env file not found"

**Problem**: Configuration not loading

**Solution**:
```bash
copy .env.example .env
# Then edit .env with your credentials
```

### Session file errors

**Problem**: Telegram session issues

**Solution**: Delete and recreate
```bash
del *.session
del *.session-journal
python main.py
# Re-authenticate when prompted
```

## Testing and Debugging

### Test in stages

1. **Test parser only**:
   ```bash
   python test_parser.py
   ```

2. **Test Telegram connection**:
   ```bash
   python dry_run.py
   ```

3. **Test broker connection**:
   ```bash
   python dashboard.py
   ```

4. **Full paper trading**:
   ```bash
   python main.py
   ```

### Enable verbose logging

Edit `.env`:
```env
LOG_LEVEL=DEBUG
```

Then check logs in `logs/` directory.

### Check logs

All activity is logged in `logs/trading_agent_YYYY-MM-DD.log`

Look for:
- Connection errors
- Parse failures
- Execution errors
- API responses

## Performance Issues

### High OpenAI costs

**Solutions**:

1. **Use cheaper model**:
   ```env
   OPENAI_MODEL=gpt-3.5-turbo
   ```

2. **Filter messages better**:
   - The quick_check in `signal_parser.py` filters first
   - Only trading messages are sent to OpenAI

### Agent too slow

**Solutions**:

1. **Check internet connection**
2. **Use faster OpenAI model** (but may be less accurate)
3. **Check broker API response times**

## Getting Help

If you're still stuck:

1. **Check all logs** in `logs/` directory
2. **Test each component individually**:
   - Parser: `python test_parser.py`
   - Telegram: `python dry_run.py`
   - Broker: `python dashboard.py`
3. **Verify all credentials** are correct
4. **Try with test/paper accounts first**

## Common .env Mistakes

❌ **Wrong**:
```env
TELEGRAM_API_ID="12345678"  # Don't use quotes
ALPACA_API_KEY = pk123      # Don't use spaces around =
BROKER=Alpaca               # Case sensitive - use lowercase
```

✅ **Correct**:
```env
TELEGRAM_API_ID=12345678
ALPACA_API_KEY=pk123
BROKER=alpaca
```

## Safety Reminders

1. ✅ Always test in paper mode first
2. ✅ Start with small position sizes
3. ✅ Monitor closely in the beginning
4. ✅ Review logs daily
5. ✅ Have a way to quickly stop the agent
6. ✅ Keep API keys secure
7. ✅ Use 2FA on all accounts

---

**Still having issues? Check `setup.md` for more detailed setup instructions.**
