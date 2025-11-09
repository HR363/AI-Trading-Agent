# ✅ Go-Live Checklist

Use this checklist before switching to live trading with real money.

## Phase 1: Setup & Testing

### Installation ✓
- [ ] Python 3.9+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] No import errors when running scripts
- [ ] `.env` file created and configured

### Credentials ✓
- [ ] Telegram API credentials working
- [ ] OpenAI API key valid (with credits)
- [ ] Broker API keys valid
- [ ] All credentials tested individually
- [ ] 2FA enabled on all accounts

### Configuration ✓
- [ ] `TRADING_MODE=paper` set
- [ ] Correct broker selected
- [ ] Correct Telegram channel ID
- [ ] Risk parameters configured
- [ ] Reviewed all settings in `.env`

## Phase 2: Component Testing

### Signal Parser ✓
- [ ] Ran `python test_parser.py`
- [ ] Tested 10+ different message formats
- [ ] Parser correctly identifies entry signals
- [ ] Parser correctly identifies partials
- [ ] Parser correctly identifies stop-loss moves
- [ ] Confidence scores seem reasonable (70%+)
- [ ] False positives are minimal

### Telegram Connection ✓
- [ ] Ran `python dry_run.py`
- [ ] Successfully connected to Telegram
- [ ] Can see messages from the channel
- [ ] Messages are being parsed correctly
- [ ] No connection errors or timeouts
- [ ] Session persists between runs

### Broker Connection ✓
- [ ] Ran `python dashboard.py`
- [ ] Can fetch account balance
- [ ] Can fetch current prices
- [ ] Prices are accurate and real-time
- [ ] API rate limits not exceeded
- [ ] No authentication errors

## Phase 3: Paper Trading

### Initial Paper Trading (Week 1) ✓
- [ ] Ran `python main.py` in paper mode
- [ ] Agent successfully opens positions
- [ ] Agent correctly sizes positions (2% default)
- [ ] Stop-losses are set properly
- [ ] Partials execute correctly
- [ ] Positions close correctly
- [ ] No crashes or errors
- [ ] Logs are comprehensive

### Performance Validation (Week 2+) ✓
- [ ] Tracked at least 20 trades
- [ ] Win rate is acceptable (>40%)
- [ ] Risk/reward is favorable
- [ ] Position sizing is appropriate
- [ ] No unexpected behavior
- [ ] Comfortable with trade execution
- [ ] Logs reviewed daily
- [ ] All edge cases handled

### Risk Management Validation ✓
- [ ] Position size limits work (2-5%)
- [ ] Max positions limit enforced (5)
- [ ] Daily loss limit triggers properly (5%)
- [ ] Confidence filtering works (≥70%)
- [ ] Agent stops when limits reached
- [ ] Risk metrics calculated correctly

## Phase 4: Strategy Validation

### Signal Quality ✓
- [ ] Signals from channel are mostly accurate
- [ ] Entry timing is reasonable
- [ ] Stop-losses are appropriate
- [ ] Take-profit levels are realistic
- [ ] False signals are rare (<10%)
- [ ] Confident in channel quality

### Execution Quality ✓
- [ ] Trades execute within 1-2 seconds
- [ ] Slippage is minimal (<0.1%)
- [ ] Orders fill reliably
- [ ] Broker fees are acceptable
- [ ] No significant execution issues
- [ ] Fills at expected prices

### Performance Metrics ✓
Record these from paper trading:
- [ ] Win Rate: _____%
- [ ] Average Profit: $____
- [ ] Average Loss: $____
- [ ] Risk/Reward Ratio: ____
- [ ] Max Drawdown: _____%
- [ ] Sharpe Ratio: ____
- [ ] Total P&L: $____

### Comfort Level ✓
- [ ] Understand how agent makes decisions
- [ ] Comfortable with trade frequency
- [ ] Comfortable with position sizes
- [ ] Trust the channel signals
- [ ] Can monitor daily
- [ ] Have time to respond to issues
- [ ] Emotionally prepared for losses

## Phase 5: Pre-Live Preparation

### Account Preparation ✓
- [ ] Funded live trading account
- [ ] Amount is money I can afford to lose
- [ ] Not using borrowed money
- [ ] Emergency fund is separate
- [ ] Comfortable with account size
- [ ] All paperwork/agreements signed

### Configuration for Live ✓
- [ ] Copied `.env` to `.env.backup`
- [ ] Set `TRADING_MODE=live` in `.env`
- [ ] Updated API endpoints to live (not testnet/paper)
- [ ] Reduced position sizes for safety (0.5-1%)
- [ ] Reduced max positions (2-3)
- [ ] Set tighter loss limits (2-3%)
- [ ] Double-checked all settings

### Safety Measures ✓
- [ ] Know how to stop agent (Ctrl+C)
- [ ] Can close positions manually on broker
- [ ] Have broker's mobile app installed
- [ ] Set up price alerts on phone
- [ ] Emergency contact for broker ready
- [ ] Written plan for emergencies

### Monitoring Setup ✓
- [ ] Logging level set to INFO or DEBUG
- [ ] Can access logs easily
- [ ] Phone notifications enabled
- [ ] Dashboard accessible (`python dashboard.py`)
- [ ] Broker app on phone
- [ ] Schedule to check multiple times daily

### Final Review ✓
- [ ] Re-read all documentation
- [ ] Understand all risks
- [ ] Have written trading plan
- [ ] Know exit strategy
- [ ] Set profit/loss targets for first month
- [ ] Documented emergency procedures
- [ ] Informed relevant people (if applicable)

## Phase 6: Initial Live Trading

### First Day ✓
- [ ] Start with smallest position sizes (0.5%)
- [ ] Monitor constantly
- [ ] Check every trade execution
- [ ] Review logs after each trade
- [ ] Verify positions on broker platform
- [ ] No issues during first day

### First Week ✓
- [ ] Check agent 3+ times daily
- [ ] Review logs daily
- [ ] Track all trades in spreadsheet
- [ ] Compare to paper trading performance
- [ ] No unexpected behavior
- [ ] Comfortable with live execution
- [ ] Risk management working properly

### First Month ✓
- [ ] Check agent 2+ times daily
- [ ] Review performance weekly
- [ ] Track vs. paper trading
- [ ] Adjust settings if needed
- [ ] Document any issues
- [ ] Calculate returns
- [ ] Decide on continuation

## Red Flags - STOP if Any Occur

🚨 **Stop immediately if:**
- [ ] Agent executes wrong trades
- [ ] Position sizing is incorrect
- [ ] Stop-losses don't trigger
- [ ] Can't stop the agent
- [ ] Losing more than expected
- [ ] Broker API errors frequent
- [ ] Execution delays significant
- [ ] Feeling stressed/anxious
- [ ] Not monitoring regularly
- [ ] Questions about legality

## Green Lights - Proceed if All True

✅ **Proceed only if:**
- [ ] ALL above checkboxes are checked
- [ ] Paper trading profitable for 2+ weeks
- [ ] Understand all risks
- [ ] Comfortable with losses
- [ ] Can monitor daily
- [ ] Using money I can lose
- [ ] Have emergency plan
- [ ] Emotionally ready

## Risk Disclosure

Before checking the box below, understand:
- ✓ Past performance ≠ future results
- ✓ Automated trading is risky
- ✓ Can lose all invested money
- ✓ Technical failures possible
- ✓ Market conditions change
- ✓ No guarantees of profit

## Final Confirmation

Date: ________________

I have:
- [ ] Completed ALL sections above
- [ ] Tested for minimum 2 weeks in paper mode
- [ ] Reviewed all documentation
- [ ] Configured all safety measures
- [ ] Understand all risks
- [ ] Am using only money I can afford to lose
- [ ] Have an emergency plan
- [ ] Am monitoring regularly
- [ ] Am emotionally prepared

Signature: ____________________

---

## Quick Reference: Going Live

### Last Steps Before Live:

1. **Backup everything**:
   ```bash
   copy .env .env.backup
   ```

2. **Update configuration**:
   ```env
   TRADING_MODE=live
   DEFAULT_POSITION_SIZE_PERCENT=0.5
   MAX_POSITION_SIZE_PERCENT=1
   MAX_OPEN_POSITIONS=2
   ```

3. **Update broker URLs**:
   - Alpaca: `https://api.alpaca.markets`
   - Binance: `BINANCE_TESTNET=false`

4. **Final test**:
   ```bash
   python dashboard.py
   ```

5. **Start live**:
   ```bash
   python main.py
   ```

6. **Monitor closely** for first hour, day, week!

### Emergency Stop:
- Press `Ctrl+C` to stop agent
- Close positions manually on broker if needed
- Change `TRADING_MODE=paper` to prevent restart

---

**Remember**: You can always go back to paper trading. There's no rush to go live. Better safe than sorry! 🛡️
