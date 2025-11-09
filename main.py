"""
AI Trading Agent - Main Entry Point

This agent monitors a Telegram trading community and automatically executes
trades based on signals from the community owner.

Features:
- Real-time Telegram message monitoring
- AI-powered signal parsing (entry, partials, stop-loss moves)
- Automatic trade execution
- Risk management (position sizing, daily loss limits)
- Support for multiple brokers (Alpaca, Binance)

Usage:
1. Copy .env.example to .env and fill in your credentials
2. Install dependencies: pip install -r requirements.txt
3. Run: python main.py
"""

import asyncio
import sys
from loguru import logger

from config.config import Config
from utils.telegram_monitor import TelegramMonitor


def print_banner():
    """Print startup banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              🤖 AI TRADING AGENT v1.0                        ║
║                                                               ║
║  Automated Trading Based on Telegram Signals                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


async def main():
    """Main entry point"""
    print_banner()
    
    logger.info("Initializing AI Trading Agent...")
    
    # Validate configuration
    if not Config.validate():
        logger.error("❌ Configuration validation failed")
        logger.error("Please check your .env file and ensure all required fields are set")
        logger.info("\nRequired fields:")
        logger.info("  - TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE")
        logger.info("  - OPENAI_API_KEY")
        logger.info(f"  - Broker credentials ({Config.BROKER.upper()})")
        return 1
    
    logger.success("✅ Configuration validated")
    
    # Show configuration
    logger.info(f"Trading Mode: {Config.TRADING_MODE.upper()}")
    logger.info(f"Broker: {Config.BROKER.upper()}")
    logger.info(f"Max Open Positions: {Config.MAX_OPEN_POSITIONS}")
    logger.info(f"Position Size: {Config.DEFAULT_POSITION_SIZE_PERCENT}%")
    logger.info(f"Max Daily Loss: {Config.MAX_DAILY_LOSS_PERCENT}%")
    
    # Warning for live trading
    if Config.TRADING_MODE == "live":
        logger.warning("⚠️  LIVE TRADING MODE ENABLED ⚠️")
        logger.warning("Real money will be used for trades!")
        
        response = input("\nAre you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Cancelled by user")
            return 0
    
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    
    try:
        # Start monitor
        monitor = TelegramMonitor()
        await monitor.start()
        
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
        return 0
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
        sys.exit(0)
