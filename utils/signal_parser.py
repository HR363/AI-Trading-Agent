import re
import json
from typing import Optional
from loguru import logger

from config.models import TradingSignal, SignalType, OrderSide
from config.config import Config
from utils.ai_client import get_ai_client

class SignalParser:
    """Parse trading signals from Telegram messages using AI"""
    
    def __init__(self):
        # AI client (OpenAI or Gemini) - lazy singleton
        self.client = get_ai_client()
        
        self.system_prompt = """You are an expert trading signal parser for SNIPE TRADING PRO channel. Your job is to extract structured trading information from trading messages.

IMPORTANT TERMINOLOGY:
- "TRIMMING" or "trim" = Taking PARTIAL profits (not closing entire position)
- "RISK FREE" or "protect positions" = Move stop loss to BREAKEVEN (entry price)
- "GOLD" = XAUUSD symbol
- "BUYING" = Long/Buy position
- "SELLING" = Short/Sell position
- "RR" = Risk-Reward ratio (e.g., "1:2 RR" means 2x profit vs risk)

Message types you'll see:
1. Entry signals: "BUYING GOLD @ MARKET ENTRY 3989.75 SL 3987.2"
2. Trim/Partial signals: "Im trimming some. Over 1:2 RR" or "You may trim"
3. Stop loss to breakeven: "risk free" or "protect positions" or "1:2 RR protect positions"
4. Alerts: "Approaching zone!!" or "PRICE APPROACHING!!"
5. Progress updates: "100 pips" or "Booom!!!" or "Running 1:2 almost"

Extract and return ONLY a valid JSON object with these fields:
{
    "signal_type": "entry|entry_alert|partial|stop_loss_move|close|unknown",
    "symbol": "XAUUSD" (convert GOLD to XAUUSD) or null,
    "side": "buy|sell" or null,
    "entry_price": 3989.75 or null,
    "entry_zone_low": null,
    "entry_zone_high": null,
    "stop_loss": 3987.2 or null,
    "take_profit_levels": [],
    "partial_percentage": 50.0 or null,
    "confidence": 0.95,
    "metadata": {"notes": "any additional context like RR ratio"}
}

Rules:
- "BUYING GOLD" → side="buy", symbol="XAUUSD"
- "SELLING GOLD" → side="sell", symbol="XAUUSD"
- "GOLD" alone → symbol="XAUUSD"
- "ENTRY 3989.75" → entry_price=3989.75, signal_type="entry"
- "SL 3987.2" → stop_loss=3987.2
- "trimming" or "trim" → signal_type="partial", partial_percentage=50.0 (default)
- "risk free" or "protect positions" → signal_type="stop_loss_move" (move SL to breakeven)
- "approaching" or "looking at" → signal_type="entry_alert"
- "1:2 RR", "1:3 RR" etc → add to metadata as {"rr_ratio": "1:2"}
- Confidence 0.9-1.0 for clear entry signals with price and SL
- Confidence 0.7-0.9 for partial/trim signals
- Confidence 0.5-0.7 for alerts/approaching
- Return ONLY the JSON object, no markdown formatting or code blocks"""

    async def parse_message(self, message: str) -> Optional[TradingSignal]:
        """Parse a trading message using AI"""
        try:
            logger.info(f"Parsing message: {message[:100]}...")
            
            # Use unified AI client (supports OpenAI and Gemini)
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message}
            ]

            result = await self.client.chat(messages, model=None, temperature=0.1, max_tokens=500)
            
            # Clean up response if it has markdown formatting
            result = result.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON response
            data = json.loads(result)
            
            # Create TradingSignal object
            signal = TradingSignal(
                signal_type=SignalType(data.get("signal_type", "unknown")),
                symbol=data.get("symbol"),
                side=OrderSide(data["side"]) if data.get("side") else None,
                entry_price=data.get("entry_price"),
                entry_zone_low=data.get("entry_zone_low"),
                entry_zone_high=data.get("entry_zone_high"),
                stop_loss=data.get("stop_loss"),
                take_profit_levels=data.get("take_profit_levels", []),
                partial_percentage=data.get("partial_percentage"),
                confidence=data.get("confidence", 0.0),
                raw_message=message,
                metadata=data.get("metadata", {})
            )
            
            logger.info(f"Parsed signal: {signal}")
            logger.info(f"Confidence: {signal.confidence:.2%}")
            
            return signal
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response was: {result}")
            return None
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None
    
    def quick_check(self, message: str) -> bool:
        """Quick check if message might contain trading signal"""
        # Keywords that indicate trading activity
        keywords = [
            'entry', 'entered', 'long', 'short', 'buy', 'sell', 'buying', 'selling',
            'partial', 'tp', 'take profit', 'stop loss', 'sl',
            'breakeven', 'be', 'close', 'closed', 'approaching',
            'getting ready', 'zone', 'position', 'gold', 'xauusd',
            'trimming', 'trim', 'risk free', 'protect', 'rr', 'pips',
            'market', 'booom'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)
