from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List

class SignalType(Enum):
    """Types of trading signals"""
    ENTRY = "entry"
    ENTRY_ALERT = "entry_alert"  # Getting ready/approaching
    PARTIAL = "partial"
    STOP_LOSS_MOVE = "stop_loss_move"
    CLOSE = "close"
    UNKNOWN = "unknown"

class OrderSide(Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"

class PositionStatus(Enum):
    """Position status"""
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"

@dataclass
class TradingSignal:
    """Parsed trading signal from Telegram message"""
    signal_type: SignalType
    symbol: Optional[str] = None
    side: Optional[OrderSide] = None
    entry_price: Optional[float] = None
    entry_zone_low: Optional[float] = None
    entry_zone_high: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit_levels: List[float] = field(default_factory=list)
    partial_percentage: Optional[float] = None
    confidence: float = 0.0
    raw_message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    
    def __str__(self):
        return f"Signal({self.signal_type.value}, {self.symbol}, {self.side})"
    
    def is_valid_entry(self) -> bool:
        """Check if signal has minimum requirements for entry"""
        return (
            self.signal_type in [SignalType.ENTRY, SignalType.ENTRY_ALERT] and
            self.symbol is not None and
            self.side is not None and
            (self.entry_price is not None or 
             (self.entry_zone_low is not None and self.entry_zone_high is not None))
        )

@dataclass
class Position:
    """Active trading position"""
    id: str
    symbol: str
    side: OrderSide
    entry_price: float
    quantity: float
    stop_loss: Optional[float] = None
    take_profit_levels: List[float] = field(default_factory=list)
    status: PositionStatus = PositionStatus.PENDING
    opened_at: datetime = field(default_factory=datetime.now)
    closed_at: Optional[datetime] = None
    pnl: float = 0.0
    original_quantity: float = 0.0
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if self.original_quantity == 0.0:
            self.original_quantity = self.quantity
    
    def calculate_pnl(self, current_price: float) -> float:
        """Calculate current PnL"""
        if self.side == OrderSide.BUY:
            self.pnl = (current_price - self.entry_price) * self.quantity
        else:
            self.pnl = (self.entry_price - current_price) * self.quantity
        return self.pnl
    
    def remaining_percentage(self) -> float:
        """Calculate remaining position percentage"""
        if self.original_quantity == 0:
            return 0.0
        return (self.quantity / self.original_quantity) * 100

@dataclass
class TradeExecution:
    """Trade execution result"""
    success: bool
    position: Optional[Position] = None
    error: Optional[str] = None
    order_id: Optional[str] = None
    executed_price: Optional[float] = None
    executed_quantity: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
