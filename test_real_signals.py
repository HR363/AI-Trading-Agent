"""
Quick test of real SNIPE TRADING PRO messages
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.signal_parser import SignalParser

# Real messages from SNIPE TRADING PRO
REAL_MESSAGES = [
    "BUYING GOLD @ MARKET ENTRY 3989.75 SL 3987.2",
    "BUYING GOLD @ MARKET ENTRY 3993. SL 3991.1",
    "Im trimming some. Over 1:2 RR ✅✅✅✅",
    "Approaching zone!!",
    "PRICE APPROACHING!! JOIN NOW!!!",
    "Looking at this zone 👀👀",
    "Booom!!! ✅✅✅",
    "I'm trimming some now 1:3 RR ✅✅✅",
    "100 pips ✅✅✅",
    "1:2 RR ✅✅✅ protect positions",
    "You may trim",
]

async def test_real_messages():
    parser = SignalParser()
    
    print("\n" + "="*70)
    print("TESTING REAL SNIPE TRADING PRO MESSAGES")
    print("="*70 + "\n")
    
    for i, message in enumerate(REAL_MESSAGES, 1):
        print(f"\n📨 Message {i}: {message}")
        print("-" * 70)
        
        # Quick check first
        if not parser.quick_check(message):
            print("❌ Quick check failed - not a trading signal")
            continue
        
        signal = await parser.parse_message(message)
        
        if signal:
            print(f"✅ Parsed: {signal.signal_type}")
            print(f"   Symbol: {signal.symbol}")
            print(f"   Side: {signal.side}")
            print(f"   Entry: {signal.entry_price}")
            print(f"   SL: {signal.stop_loss}")
            print(f"   Confidence: {signal.confidence:.0%}")
            
            if signal.confidence >= 0.7:
                print(f"   🎯 WOULD EXECUTE (confidence >= 70%)")
            else:
                print(f"   ⚠️  Would NOT execute (confidence < 70%)")
        else:
            print("❌ Failed to parse")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(test_real_messages())
