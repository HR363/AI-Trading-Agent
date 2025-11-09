from typing import Dict, Optional, List
from datetime import datetime, timedelta
from loguru import logger

from config.models import Position, TradingSignal, SignalType, PositionStatus, TradeExecution
from brokers.broker_interface import BrokerInterface
from config.config import Config

class PositionManager:
    """Manage open positions and risk"""
    
    def __init__(self, broker: BrokerInterface):
        self.broker = broker
        self.positions: Dict[str, Position] = {}
        self.daily_pnl = 0.0
        self.daily_reset_time = datetime.now()
        
    async def can_open_position(self) -> tuple[bool, str]:
        """Check if we can open a new position"""
        
        # Check max open positions
        open_positions = [p for p in self.positions.values() if p.status == PositionStatus.OPEN]
        if len(open_positions) >= Config.MAX_OPEN_POSITIONS:
            return False, f"Max open positions reached ({Config.MAX_OPEN_POSITIONS})"
        
        # Check daily loss limit
        if self._should_reset_daily_pnl():
            self._reset_daily_pnl()
        
        balance = await self.broker.get_account_balance()
        max_loss = balance * (Config.MAX_DAILY_LOSS_PERCENT / 100)
        
        if self.daily_pnl <= -max_loss:
            return False, f"Daily loss limit reached ({Config.MAX_DAILY_LOSS_PERCENT}%)"
        
        return True, "OK"
    
    async def execute_signal(self, signal: TradingSignal) -> Optional[TradeExecution]:
        """Execute a trading signal"""
        
        if signal.signal_type == SignalType.ENTRY:
            return await self._handle_entry(signal)
        elif signal.signal_type == SignalType.PARTIAL:
            return await self._handle_partial(signal)
        elif signal.signal_type == SignalType.STOP_LOSS_MOVE:
            return await self._handle_stop_loss_move(signal)
        elif signal.signal_type == SignalType.CLOSE:
            return await self._handle_close(signal)
        elif signal.signal_type == SignalType.ENTRY_ALERT:
            logger.info(f"Entry alert for {signal.symbol} - monitoring for entry")
            return None
        
        return None
    
    async def _handle_entry(self, signal: TradingSignal) -> Optional[TradeExecution]:
        """Handle entry signal"""
        
        # Validate signal
        if not signal.is_valid_entry():
            logger.warning(f"Invalid entry signal: {signal}")
            return None
        
        # Check if we can open position
        can_open, reason = await self.can_open_position()
        if not can_open:
            logger.warning(f"Cannot open position: {reason}")
            return None
        
        # Check confidence threshold
        if signal.confidence < 0.7:
            logger.warning(f"Signal confidence too low: {signal.confidence:.2%}")
            return None
        
        # Calculate position size
        balance = await self.broker.get_account_balance()
        position_size = balance * (Config.DEFAULT_POSITION_SIZE_PERCENT / 100)
        
        # Limit to max position size
        max_size = balance * (Config.MAX_POSITION_SIZE_PERCENT / 100)
        position_size = min(position_size, max_size)
        
        logger.info(f"Opening position: {signal.symbol} {signal.side.value}")
        logger.info(f"Position size: ${position_size:.2f}")
        
        # Execute trade
        execution = await self.broker.execute_trade(signal, position_size)
        
        if execution.success and execution.position:
            self.positions[execution.position.id] = execution.position
            logger.success(f"Position opened: {execution.position}")
        else:
            logger.error(f"Failed to open position: {execution.error}")
        
        return execution
    
    async def _handle_partial(self, signal: TradingSignal) -> Optional[TradeExecution]:
        """Handle partial profit taking"""
        
        if not signal.symbol:
            logger.warning("Partial signal missing symbol")
            return None
        
        # Find matching position
        position = self._find_position_by_symbol(signal.symbol)
        if not position:
            logger.warning(f"No open position found for {signal.symbol}")
            return None
        
        percentage = signal.partial_percentage or 50.0
        logger.info(f"Taking {percentage}% partial on {signal.symbol}")
        
        execution = await self.broker.close_position(position, percentage)
        
        if execution.success:
            # Update daily PnL
            current_price = await self.broker.get_current_price(signal.symbol)
            if current_price:
                pnl = position.calculate_pnl(current_price)
                self.daily_pnl += pnl * (percentage / 100.0)
            
            logger.success(f"Partial closed: {percentage}% of {signal.symbol}")
        else:
            logger.error(f"Failed to close partial: {execution.error}")
        
        return execution
    
    async def _handle_stop_loss_move(self, signal: TradingSignal) -> Optional[TradeExecution]:
        """Handle stop loss move"""
        
        if not signal.symbol:
            logger.warning("Stop loss move signal missing symbol")
            return None
        
        position = self._find_position_by_symbol(signal.symbol)
        if not position:
            logger.warning(f"No open position found for {signal.symbol}")
            return None
        
        # Determine new stop loss
        new_sl = signal.stop_loss
        
        # If signal says "breakeven" but doesn't specify price, use entry price
        if signal.metadata.get("breakeven") and not new_sl:
            new_sl = position.entry_price
        
        if not new_sl:
            logger.warning("Could not determine new stop loss price")
            return None
        
        logger.info(f"Moving stop loss for {signal.symbol} to {new_sl}")
        
        success = await self.broker.update_stop_loss(position, new_sl)
        
        if success:
            logger.success(f"Stop loss moved to {new_sl}")
        else:
            logger.error("Failed to move stop loss")
        
        return None
    
    async def _handle_close(self, signal: TradingSignal) -> Optional[TradeExecution]:
        """Handle position close"""
        
        if not signal.symbol:
            logger.warning("Close signal missing symbol")
            return None
        
        position = self._find_position_by_symbol(signal.symbol)
        if not position:
            logger.warning(f"No open position found for {signal.symbol}")
            return None
        
        logger.info(f"Closing position: {signal.symbol}")
        
        execution = await self.broker.close_position(position, 100.0)
        
        if execution.success:
            # Update daily PnL
            current_price = await self.broker.get_current_price(signal.symbol)
            if current_price:
                pnl = position.calculate_pnl(current_price)
                self.daily_pnl += pnl
            
            # Remove from active positions
            if position.id in self.positions:
                del self.positions[position.id]
            
            logger.success(f"Position closed: {signal.symbol}, PnL: ${pnl:.2f}")
        else:
            logger.error(f"Failed to close position: {execution.error}")
        
        return execution
    
    def _find_position_by_symbol(self, symbol: str) -> Optional[Position]:
        """Find an open position by symbol"""
        for position in self.positions.values():
            if position.symbol == symbol and position.status == PositionStatus.OPEN:
                return position
        return None
    
    def _should_reset_daily_pnl(self) -> bool:
        """Check if we should reset daily PnL"""
        return datetime.now() - self.daily_reset_time > timedelta(days=1)
    
    def _reset_daily_pnl(self):
        """Reset daily PnL counter"""
        self.daily_pnl = 0.0
        self.daily_reset_time = datetime.now()
        logger.info("Daily PnL reset")
    
    async def get_portfolio_status(self) -> dict:
        """Get current portfolio status"""
        balance = await self.broker.get_account_balance()
        open_positions = [p for p in self.positions.values() if p.status == PositionStatus.OPEN]
        
        total_pnl = sum([
            p.calculate_pnl(await self.broker.get_current_price(p.symbol) or 0)
            for p in open_positions
        ])
        
        return {
            "balance": balance,
            "open_positions": len(open_positions),
            "daily_pnl": self.daily_pnl,
            "total_unrealized_pnl": total_pnl,
            "positions": [
                {
                    "symbol": p.symbol,
                    "side": p.side.value,
                    "quantity": p.quantity,
                    "entry_price": p.entry_price,
                    "pnl": p.pnl
                }
                for p in open_positions
            ]
        }
