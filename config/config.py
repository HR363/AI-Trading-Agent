import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class Config:
    """Configuration class for the trading agent"""
    
    # Telegram Configuration
    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
    TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
    
    # OpenAI Configuration
    # AI Provider Configuration
    # Set AI_PROVIDER to 'openai' or 'gemini'
    AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    # Gemini (Google) Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "chat-bison@001")
    
    # Trading Configuration
    TRADING_MODE = os.getenv("TRADING_MODE", "paper").lower()
    BROKER = os.getenv("BROKER", "alpaca").lower()
    
    # Alpaca Configuration
    ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
    ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
    ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    
    # Binance Configuration
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
    BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
    
    # MT5 Configuration
    MT5_ACCOUNT = os.getenv("MT5_ACCOUNT")
    MT5_PASSWORD = os.getenv("MT5_PASSWORD")
    MT5_SERVER = os.getenv("MT5_SERVER")
    MT5_PATH = os.getenv("MT5_PATH", "C:\\Program Files\\MetaTrader 5\\terminal64.exe")
    
    # Risk Management
    DEFAULT_POSITION_SIZE_PERCENT = float(os.getenv("DEFAULT_POSITION_SIZE_PERCENT", "2"))
    MAX_POSITION_SIZE_PERCENT = float(os.getenv("MAX_POSITION_SIZE_PERCENT", "5"))
    MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "5"))
    MAX_DAILY_LOSS_PERCENT = float(os.getenv("MAX_DAILY_LOSS_PERCENT", "5"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_fields = {
            "Telegram": [cls.TELEGRAM_API_ID, cls.TELEGRAM_API_HASH, cls.TELEGRAM_PHONE],
            "OpenAI": [cls.OPENAI_API_KEY],
        }
        
        if cls.BROKER == "alpaca":
            required_fields["Alpaca"] = [cls.ALPACA_API_KEY, cls.ALPACA_SECRET_KEY]
        elif cls.BROKER == "binance":
            required_fields["Binance"] = [cls.BINANCE_API_KEY, cls.BINANCE_SECRET_KEY]
        elif cls.BROKER == "mt5":
            required_fields["MT5"] = [cls.MT5_ACCOUNT, cls.MT5_PASSWORD, cls.MT5_SERVER]
        
        missing = []
        for service, fields in required_fields.items():
            if not all(fields):
                missing.append(service)
        
        if missing:
            logger.error(f"Missing configuration for: {', '.join(missing)}")
            logger.error("Please check your .env file")
            return False
        
        return True

# Configure logging
logger.add(
    "logs/trading_agent_{time}.log",
    rotation="1 day",
    retention="30 days",
    level=Config.LOG_LEVEL
)
