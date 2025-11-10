"""
Test MT5 Connection - Verify your MetaTrader 5 setup

This script tests the connection to your MT5 account and displays
account information.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from brokers.mt5_broker import MT5Broker
from config.config import Config
from loguru import logger

async def test_mt5_connection():
    """Test MT5 connection and display account info"""
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              MT5 CONNECTION TEST                              ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # Validate configuration
    print("📋 Checking configuration...")
    if not all([Config.MT5_ACCOUNT, Config.MT5_PASSWORD, Config.MT5_SERVER]):
        print("❌ Missing MT5 credentials in .env file!")
        print("\nRequired variables:")
        print("  - MT5_ACCOUNT")
        print("  - MT5_PASSWORD")
        print("  - MT5_SERVER")
        return
    
    print(f"   Account: {Config.MT5_ACCOUNT}")
    print(f"   Server: {Config.MT5_SERVER}")
    print()
    
    # Create broker instance
    print("🔗 Connecting to MT5...")
    broker = MT5Broker()
    
    # Test connection
    connected = await broker.connect()
    
    if not connected:
        print("\n❌ Connection failed!")
        print("\nTroubleshooting:")
        print("1. Make sure MetaTrader 5 is installed")
        print("2. Verify your account credentials are correct")
        print("3. Check if the MT5 terminal is running")
        print("4. Ensure the server name is exact (case-sensitive)")
        print("5. For demo accounts, make sure you're using the demo server")
        return
    
    print("\n✅ Connection successful!\n")
    
    # Get account information
    print("=" * 70)
    print("📊 ACCOUNT INFORMATION")
    print("=" * 70)
    
    balance = await broker.get_account_balance()
    buying_power = await broker.get_buying_power()
    
    print(f"\n💰 Balance: ${balance:,.2f}")
    print(f"💵 Free Margin (Buying Power): ${buying_power:,.2f}")
    
    if broker.account_info:
        print(f"📈 Equity: ${broker.account_info.equity:,.2f}")
        print(f"📊 Margin Used: ${broker.account_info.margin:,.2f}")
        print(f"🎚️  Margin Level: {broker.account_info.margin_level:.2f}%")
        print(f"⚖️  Leverage: 1:{broker.account_info.leverage}")
        print(f"💼 Currency: {broker.account_info.currency}")
        print(f"🏢 Company: {broker.account_info.company}")
        print(f"👤 Name: {broker.account_info.name}")
    
    # Get open positions
    print("\n" + "=" * 70)
    print("📋 OPEN POSITIONS")
    print("=" * 70)
    
    positions = await broker.get_open_positions()
    
    if positions:
        print(f"\n Found {len(positions)} open position(s):\n")
        for i, pos in enumerate(positions, 1):
            print(f"{i}. {pos.symbol}")
            print(f"   Side: {pos.side}")
            print(f"   Quantity: {pos.quantity}")
            print(f"   Entry: ${pos.entry_price:.5f}")
            print(f"   Current: ${pos.current_price:.5f}")
            print(f"   P&L: ${pos.unrealized_pnl:.2f}")
            if pos.stop_loss:
                print(f"   Stop Loss: ${pos.stop_loss:.5f}")
            if pos.take_profit:
                print(f"   Take Profit: ${pos.take_profit:.5f}")
            print()
    else:
        print("\n No open positions")
    
    # Test getting price for common symbols
    print("\n" + "=" * 70)
    print("💱 PRICE TEST (Common Symbols)")
    print("=" * 70)
    
    test_symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
    
    for symbol in test_symbols:
        price = await broker.get_current_price(symbol)
        if price:
            print(f"   {symbol}: ${price:.5f}")
        else:
            print(f"   {symbol}: Not available")
    
    # Disconnect
    await broker.disconnect()
    
    print("\n" + "=" * 70)
    print("✅ MT5 Setup Complete!")
    print("=" * 70)
    print("\nYour MT5 integration is working correctly.")
    print("You can now run the trading agent with: python main.py")

def main():
    """Main entry point"""
    try:
        asyncio.run(test_mt5_connection())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        logger.exception(f"Error during test: {e}")
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
