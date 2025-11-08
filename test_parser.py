"""
Test Signal Parser - Test the AI signal parsing without executing trades

This script lets you test how the agent interprets different message formats.
"""

import asyncio
from signal_parser import SignalParser
from config import Config
from loguru import logger

# Example messages to test
TEST_MESSAGES = [
    "I just entered BTCUSDT long at 45000",
    "Getting ready to enter ETH around 2500-2520",
    "Took 50% partial at 46000",
    "Moving stop loss to breakeven",
    "Just entered AAPL short at 180.50, SL 182, TP 178, 175",
    "Closed my position on TSLA",
    "Price is approaching our entry zone",
    "I'm in GOOGL long at 140, stop at 138, targets 142, 145, 148",
]

async def test_parser():
    """Test the signal parser with example messages"""
    
    print("🧪 Testing Signal Parser\n")
    print("="*80)
    
    if not Config.OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not set in .env file")
        print("Please copy .env.example to .env and add your OpenAI API key")
        return
    
    parser = SignalParser()
    
    for i, message in enumerate(TEST_MESSAGES, 1):
        print(f"\n📨 Test {i}: {message}")
        print("-"*80)
        
        signal = await parser.parse_message(message)
        
        if signal:
            print(f"✅ Parsed Successfully!")
            print(f"   Type: {signal.signal_type.value}")
            print(f"   Symbol: {signal.symbol}")
            print(f"   Side: {signal.side.value if signal.side else 'N/A'}")
            print(f"   Entry Price: {signal.entry_price}")
            print(f"   Entry Zone: {signal.entry_zone_low} - {signal.entry_zone_high}")
            print(f"   Stop Loss: {signal.stop_loss}")
            print(f"   Take Profits: {signal.take_profit_levels}")
            print(f"   Partial %: {signal.partial_percentage}")
            print(f"   Confidence: {signal.confidence:.1%}")
            
            if signal.is_valid_entry():
                print(f"   ✅ Valid entry signal - would be executed")
            elif signal.signal_type.value != "unknown":
                print(f"   ℹ️  Valid {signal.signal_type.value} signal")
            else:
                print(f"   ⚠️  Not a trading signal")
        else:
            print(f"❌ Failed to parse")
        
        print("="*80)
    
    print("\n✅ All tests completed!")
    print("\nTips:")
    print("- Messages with confidence < 70% won't be executed")
    print("- Entry signals need symbol, side, and entry price/zone")
    print("- You can modify TEST_MESSAGES above to test your own formats")

async def test_custom_message():
    """Test a custom message"""
    print("\n🧪 Custom Message Testing\n")
    print("Enter your message (or 'quit' to exit):")
    print("Example: I entered BTCUSDT long at 45000, SL 44500\n")
    
    parser = SignalParser()
    
    while True:
        message = input("\nMessage: ").strip()
        
        if message.lower() in ['quit', 'exit', 'q']:
            break
        
        if not message:
            continue
        
        print("\n" + "="*80)
        signal = await parser.parse_message(message)
        
        if signal:
            print(f"✅ Signal Type: {signal.signal_type.value}")
            print(f"   Symbol: {signal.symbol}")
            print(f"   Side: {signal.side.value if signal.side else 'N/A'}")
            print(f"   Entry: {signal.entry_price}")
            print(f"   Stop Loss: {signal.stop_loss}")
            print(f"   Confidence: {signal.confidence:.1%}")
            
            if signal.is_valid_entry() and signal.confidence >= 0.7:
                print(f"\n   ✅ This would be EXECUTED by the agent")
            elif signal.confidence < 0.7:
                print(f"\n   ⚠️  Confidence too low (need ≥70%)")
            else:
                print(f"\n   ℹ️  Valid signal but not an entry")
        else:
            print("❌ Failed to parse")
        
        print("="*80)

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                 Signal Parser Test Suite                      ║
╚═══════════════════════════════════════════════════════════════╝

This tool helps you test how the AI interprets trading messages.
""")
    
    print("Choose an option:")
    print("1. Test predefined examples")
    print("2. Test your own messages")
    print("3. Both")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(test_parser())
    elif choice == "2":
        asyncio.run(test_custom_message())
    elif choice == "3":
        asyncio.run(test_parser())
        asyncio.run(test_custom_message())
    else:
        print("Invalid choice")
