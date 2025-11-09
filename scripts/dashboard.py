"""
Portfolio Dashboard - View current trading status

Quick script to check your account balance, open positions, and trading status.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add parent directory to path to import from brokers and config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config
from brokers.broker_interface import get_broker

async def show_dashboard():
    """Display portfolio dashboard"""
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                   PORTFOLIO DASHBOARD                         ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # Validate config
    if not Config.validate():
        print("❌ Configuration error - check your .env file\n")
        return
    
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Mode: {Config.TRADING_MODE.upper()}")
    print(f"🏦 Broker: {Config.BROKER.upper()}")
    print("="*80 + "\n")
    
    try:
        # Get broker
        broker = get_broker()
        
        # Account balance
        print("💰 ACCOUNT BALANCE")
        print("-"*80)
        balance = await broker.get_account_balance()
        print(f"   Total Equity: ${balance:,.2f}\n")
        
        # Position sizing info
        default_size = balance * (Config.DEFAULT_POSITION_SIZE_PERCENT / 100)
        max_size = balance * (Config.MAX_POSITION_SIZE_PERCENT / 100)
        
        print("📊 POSITION SIZING")
        print("-"*80)
        print(f"   Default per trade: ${default_size:,.2f} ({Config.DEFAULT_POSITION_SIZE_PERCENT}%)")
        print(f"   Maximum per trade: ${max_size:,.2f} ({Config.MAX_POSITION_SIZE_PERCENT}%)")
        print(f"   Max open positions: {Config.MAX_OPEN_POSITIONS}")
        print(f"   Daily loss limit: ${balance * (Config.MAX_DAILY_LOSS_PERCENT / 100):,.2f} ({Config.MAX_DAILY_LOSS_PERCENT}%)\n")
        
        # Open positions
        print("📈 OPEN POSITIONS")
        print("-"*80)
        positions = await broker.get_open_positions()
        
        if positions:
            print(f"   {len(positions)} position(s) open:\n")
            
            total_pnl = 0.0
            for i, pos in enumerate(positions, 1):
                print(f"   {i}. {pos.symbol}")
                print(f"      Side: {pos.side.value.upper()}")
                print(f"      Quantity: {pos.quantity}")
                print(f"      Entry: ${pos.entry_price:.2f}")
                
                if pos.stop_loss:
                    print(f"      Stop Loss: ${pos.stop_loss:.2f}")
                
                # Get current price and calculate PnL
                current_price = await broker.get_current_price(pos.symbol)
                if current_price:
                    pnl = pos.calculate_pnl(current_price)
                    pnl_percent = (pnl / (pos.entry_price * pos.quantity)) * 100
                    total_pnl += pnl
                    
                    pnl_symbol = "📈" if pnl > 0 else "📉" if pnl < 0 else "➡️"
                    print(f"      Current: ${current_price:.2f}")
                    print(f"      P&L: {pnl_symbol} ${pnl:,.2f} ({pnl_percent:+.2f}%)")
                
                print()
            
            print(f"   Total Unrealized P&L: ${total_pnl:,.2f}")
        else:
            print("   No open positions\n")
        
        # Risk metrics
        print("\n⚠️  RISK METRICS")
        print("-"*80)
        
        if positions:
            total_exposure = sum(p.entry_price * p.quantity for p in positions)
            exposure_percent = (total_exposure / balance) * 100
            print(f"   Total Exposure: ${total_exposure:,.2f} ({exposure_percent:.1f}%)")
        else:
            print(f"   Total Exposure: $0.00 (0%)")
        
        print(f"   Available for new trades: {Config.MAX_OPEN_POSITIONS - len(positions)} position(s)")
        
        print("\n" + "="*80)
        print("\n✅ Dashboard loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error loading dashboard: {e}")
        logger.error(f"Dashboard error: {e}", exc_info=True)


async def test_price_feed():
    """Test price feed for common symbols"""
    print("\n\n📊 Testing Price Feed")
    print("="*80 + "\n")
    
    symbols = []
    
    if Config.BROKER == "binance":
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    else:
        symbols = ["AAPL", "TSLA", "GOOGL"]
    
    try:
        broker = get_broker()
        
        print(f"Testing {Config.BROKER.upper()} price feed:\n")
        
        for symbol in symbols:
            price = await broker.get_current_price(symbol)
            if price:
                print(f"   {symbol}: ${price:,.2f} ✅")
            else:
                print(f"   {symbol}: Failed to get price ❌")
        
        print("\n✅ Price feed test complete")
        
    except Exception as e:
        print(f"❌ Error testing price feed: {e}")


async def main():
    """Main entry point"""
    
    await show_dashboard()
    
    # Ask if user wants to test price feed
    print("\n" + "="*80)
    test = input("\nTest price feed? (y/n): ").lower().strip()
    
    if test == 'y':
        await test_price_feed()
    
    print("\n👋 Done!\n")


if __name__ == "__main__":
    asyncio.run(main())
