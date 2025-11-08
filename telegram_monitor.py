import asyncio
from telethon import TelegramClient, events
from loguru import logger

from config import Config
from signal_parser import SignalParser
from position_manager import PositionManager
from broker_interface import get_broker

class TelegramMonitor:
    """Monitor Telegram channel for trading signals"""
    
    def __init__(self):
        self.client = TelegramClient(
            'trading_agent_session',
            Config.TELEGRAM_API_ID,
            Config.TELEGRAM_API_HASH
        )
        
        self.parser = SignalParser()
        self.broker = get_broker()
        self.position_manager = PositionManager(self.broker)
        
        self.is_running = False
        
    async def start(self):
        """Start monitoring Telegram channel"""
        logger.info("Starting Telegram monitor...")
        
        # Connect to Telegram
        await self.client.start(phone=Config.TELEGRAM_PHONE)
        logger.success("Connected to Telegram")
        
        # Verify channel access
        try:
            channel = await self.client.get_entity(Config.TELEGRAM_CHANNEL_ID)
            logger.info(f"Monitoring channel: {channel.title}")
        except Exception as e:
            logger.error(f"Could not access channel: {e}")
            logger.error(f"Channel ID: {Config.TELEGRAM_CHANNEL_ID}")
            return
        
        # Register event handler
        @self.client.on(events.NewMessage(chats=Config.TELEGRAM_CHANNEL_ID))
        async def handle_message(event):
            await self._handle_new_message(event)
        
        self.is_running = True
        logger.success("Trading agent is now active!")
        logger.info(f"Mode: {Config.TRADING_MODE.upper()}")
        logger.info(f"Broker: {Config.BROKER.upper()}")
        
        # Show portfolio status
        status = await self.position_manager.get_portfolio_status()
        logger.info(f"Account Balance: ${status['balance']:.2f}")
        logger.info(f"Open Positions: {status['open_positions']}")
        
        # Keep running
        try:
            await self.client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            await self.stop()
    
    async def _handle_new_message(self, event):
        """Handle new message from Telegram channel"""
        try:
            message = event.message.message
            
            # Skip empty messages
            if not message or len(message.strip()) == 0:
                return
            
            logger.info("="*80)
            logger.info(f"New message: {message[:200]}")
            
            # Quick check if message might be a signal
            if not self.parser.quick_check(message):
                logger.debug("Message doesn't appear to be a trading signal")
                return
            
            # Parse message with AI
            signal = await self.parser.parse_message(message)
            
            if not signal:
                logger.warning("Failed to parse signal")
                return
            
            if signal.signal_type == SignalType.UNKNOWN:
                logger.info("Message parsed but not a trading signal")
                return
            
            # Check confidence threshold
            if signal.confidence < 0.5:
                logger.warning(f"Signal confidence too low: {signal.confidence:.2%}")
                return
            
            logger.success(f"Signal detected: {signal}")
            
            # Execute signal
            execution = await self.position_manager.execute_signal(signal)
            
            if execution:
                if execution.success:
                    logger.success(f"✅ Trade executed successfully!")
                    if execution.position:
                        logger.info(f"Position: {execution.position.symbol}")
                        logger.info(f"Price: ${execution.executed_price:.2f}")
                        logger.info(f"Quantity: {execution.executed_quantity}")
                else:
                    logger.error(f"❌ Trade failed: {execution.error}")
            
            # Show updated portfolio
            status = await self.position_manager.get_portfolio_status()
            logger.info(f"Portfolio - Balance: ${status['balance']:.2f}, "
                       f"Open: {status['open_positions']}, "
                       f"Daily PnL: ${status['daily_pnl']:.2f}")
            
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def stop(self):
        """Stop monitoring"""
        logger.info("Stopping Telegram monitor...")
        self.is_running = False
        await self.client.disconnect()
        logger.info("Disconnected")


async def main():
    """Main entry point"""
    
    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Please check your .env file")
        return
    
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Start monitor
    monitor = TelegramMonitor()
    await monitor.start()


if __name__ == "__main__":
    asyncio.run(main())
