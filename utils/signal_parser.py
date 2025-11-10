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
        
        self.system_prompt = """You are an expert trading signal parser. Your job is to extract structured trading information from informal trading messages.

The user will send you messages from a trading community that may contain:
1. Entry signals: "I entered BTCUSDT long at 45000" or "Getting ready for entry around 45000-45200"
2. Partial profit taking: "Took 50% off at 46000" or "Closing half position"
3. Stop loss moves: "Moving SL to breakeven" or "SL moved to entry"
4. Position updates: "Price approaching entry zone"

Extract and return ONLY a valid JSON object with these fields:
{
    "signal_type": "entry|entry_alert|partial|stop_loss_move|close|unknown",
    "symbol": "BTCUSDT" or null,
    "side": "buy|sell" or null,
    "entry_price": 45000.0 or null,
    "entry_zone_low": 45000.0 or null,
    "entry_zone_high": 45200.0 or null,
    "stop_loss": 44000.0 or null,
    "take_profit_levels": [46000, 47000] or [],
    "partial_percentage": 50.0 or null,
    "confidence": 0.95,
    "metadata": {"notes": "any additional context"}
}

Rules:
- For "long" positions, side is "buy". For "short" positions, side is "sell"
- If message says "getting ready" or "approaching", use signal_type "entry_alert"
- If message says "entered" or "taking position", use signal_type "entry"
- Confidence should be 0.0-1.0 based on clarity of the message
- Extract all numerical values (prices, percentages)
- If stop loss is "breakeven" or "BE", set it to entry_price
- Common symbols: BTC, ETH, AAPL, TSLA, etc. Add common suffixes like USDT, USD, /USD
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
            'entry', 'entered', 'long', 'short', 'buy', 'sell',
            'partial', 'tp', 'take profit', 'stop loss', 'sl',
            'breakeven', 'be', 'close', 'closed', 'approaching',
            'getting ready', 'zone', 'position'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)
