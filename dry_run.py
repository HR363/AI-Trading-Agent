"""
Dry Run Monitor - Monitor Telegram without executing trades

This script connects to your Telegram channel and shows what trades
the agent WOULD execute, but doesn't actually execute them.

Perfect for testing and validating signal parsing before going live.
"""

import asyncio
from telethon import TelegramClient, events
from loguru import logger

from config import Config
from signal_parser import SignalParser
from models import SignalType

class DryRunMonitor:
    """Monitor Telegram channel in dry-run mode"""
    
    def __init__(self):
        self.client = TelegramClient(
            'trading_agent_session',
            Config.TELEGRAM_API_ID,
            Config.TELEGRAM_API_HASH
        )
        
        self.parser = SignalParser()
        self.trade_count = 0
        self.signal_count = 0
        
    async def start(self):
        """Start monitoring"""
        logger.info("Starting Dry Run Monitor...")
        logger.info("This will show what trades WOULD be executed")
        logger.info("No actual trades will be placed\n")
        
        # Connect
        await self.client.start(phone=Config.TELEGRAM_PHONE)
        logger.success("Connected to Telegram")
        
        # Verify channel
        try:
            channel = await self.client.get_entity(Config.TELEGRAM_CHANNEL_ID)
            logger.info(f"Monitoring channel: {channel.title}\n")
            logger.info("="*80)
        except Exception as e:
            logger.error(f"Could not access channel: {e}")
            return
        
        # Register handler
        @self.client.on(events.NewMessage(chats=Config.TELEGRAM_CHANNEL_ID))
        async def handle_message(event):
            await self._handle_message(event)
        
        logger.success("🟢 Dry Run Monitor Active!")
        logger.info("Watching for signals...\n")
        
        # Keep running
        try:
            await self.client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("\nStopping...")
            await self.client.disconnect()
    
    async def _handle_message(self, event):
        """Handle new message"""
        try:
            message = event.message.message
            
            if not message or len(message.strip()) == 0:
                return
            
            logger.info("="*80)
            logger.info(f"📨 New Message:")
            logger.info(f"   {message[:200]}")
            
            # Quick check
            if not self.parser.quick_check(message):
                logger.debug("   ℹ️  Not a trading signal\n")
                return
            
            # Parse
            signal = await self.parser.parse_message(message)
            
            if not signal or signal.signal_type == SignalType.UNKNOWN:
                logger.info("   ℹ️  Not a trading signal\n")
                return
            
            self.signal_count += 1
            
            # Show parsed signal
            logger.success(f"\n✅ Signal Detected:")
            logger.info(f"   Type: {signal.signal_type.value.upper()}")
            logger.info(f"   Symbol: {signal.symbol}")
            logger.info(f"   Side: {signal.side.value if signal.side else 'N/A'}")
            
            if signal.entry_price:
                logger.info(f"   Entry Price: ${signal.entry_price}")
            if signal.entry_zone_low and signal.entry_zone_high:
                logger.info(f"   Entry Zone: ${signal.entry_zone_low} - ${signal.entry_zone_high}")
            if signal.stop_loss:
                logger.info(f"   Stop Loss: ${signal.stop_loss}")
            if signal.take_profit_levels:
                logger.info(f"   Take Profits: {signal.take_profit_levels}")
            if signal.partial_percentage:
                logger.info(f"   Partial %: {signal.partial_percentage}%")
            
            logger.info(f"   Confidence: {signal.confidence:.1%}")
            
            # Check if would be executed
            would_execute = False
            reason = ""
            
            if signal.signal_type == SignalType.ENTRY:
                if not signal.is_valid_entry():
                    reason = "Missing required fields"
                elif signal.confidence < 0.7:
                    reason = f"Confidence too low ({signal.confidence:.1%} < 70%)"
                else:
                    would_execute = True
                    self.trade_count += 1
            elif signal.signal_type in [SignalType.PARTIAL, SignalType.STOP_LOSS_MOVE, SignalType.CLOSE]:
                if signal.confidence >= 0.5:
                    would_execute = True
            elif signal.signal_type == SignalType.ENTRY_ALERT:
                logger.info(f"\n   📌 ENTRY ALERT - Would monitor for entry")
            
            # Show result
            if would_execute:
                logger.success(f"\n   🟢 WOULD EXECUTE THIS TRADE")
                if signal.signal_type == SignalType.ENTRY:
                    position_size = Config.DEFAULT_POSITION_SIZE_PERCENT
                    logger.info(f"   💰 Position Size: {position_size}% of portfolio")
                    logger.info(f"   📊 Max Open Positions: {Config.MAX_OPEN_POSITIONS}")
            else:
                logger.warning(f"\n   🟡 WOULD NOT EXECUTE: {reason}")
            
            # Summary
            logger.info(f"\n📊 Session Stats:")
            logger.info(f"   Signals Detected: {self.signal_count}")
            logger.info(f"   Would Execute: {self.trade_count}")
            logger.info("="*80 + "\n")
            
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)


async def main():
    """Main entry point"""
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                     DRY RUN MONITOR                           ║
║                                                               ║
║  Monitor Telegram signals without executing trades           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # Validate config
    if not Config.validate():
        logger.error("Configuration validation failed")
        logger.info("\nRequired:")
        logger.info("  - TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE")
        logger.info("  - TELEGRAM_CHANNEL_ID")
        logger.info("  - OPENAI_API_KEY")
        return
    
    logger.success("✅ Configuration OK")
    logger.info(f"Position Size: {Config.DEFAULT_POSITION_SIZE_PERCENT}%")
    logger.info(f"Max Positions: {Config.MAX_OPEN_POSITIONS}")
    logger.info(f"Confidence Threshold: 70%\n")
    
    # Start monitor
    monitor = DryRunMonitor()
    await monitor.start()


if __name__ == "__main__":
    asyncio.run(main())
