from abc import ABC, abstractmethod
from typing import Optional, List
from loguru import logger

from models import TradingSignal, Position, TradeExecution, OrderSide, PositionStatus
from config import Config

class BrokerInterface(ABC):
    """Abstract base class for broker integrations"""
    
    @abstractmethod
    async def get_account_balance(self) -> float:
        """Get current account balance"""
        pass
    
    @abstractmethod
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price for symbol"""
        pass
    
    @abstractmethod
    async def execute_trade(self, signal: TradingSignal, position_size: float) -> TradeExecution:
        """Execute a trade based on signal"""
        pass
    
    @abstractmethod
    async def close_position(self, position: Position, percentage: float = 100.0) -> TradeExecution:
        """Close a position (full or partial)"""
        pass
    
    @abstractmethod
    async def update_stop_loss(self, position: Position, new_stop_loss: float) -> bool:
        """Update stop loss for a position"""
        pass
    
    @abstractmethod
    async def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        pass


class AlpacaBroker(BrokerInterface):
    """Alpaca broker implementation for stocks/forex"""
    
    def __init__(self):
        try:
            from alpaca_trade_api import REST
            self.api = REST(
                Config.ALPACA_API_KEY,
                Config.ALPACA_SECRET_KEY,
                Config.ALPACA_BASE_URL
            )
            logger.info("Alpaca broker initialized")
        except ImportError:
            logger.error("alpaca-trade-api not installed. Run: pip install alpaca-trade-api")
            raise
    
    async def get_account_balance(self) -> float:
        try:
            account = self.api.get_account()
            return float(account.equity)
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return 0.0
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        try:
            # Remove common crypto suffixes for stock symbols
            clean_symbol = symbol.replace("USDT", "").replace("USD", "")
            quote = self.api.get_latest_trade(clean_symbol)
            return float(quote.price)
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    async def execute_trade(self, signal: TradingSignal, position_size: float) -> TradeExecution:
        try:
            clean_symbol = signal.symbol.replace("USDT", "").replace("USD", "")
            
            # Calculate quantity
            current_price = await self.get_current_price(clean_symbol)
            if not current_price:
                return TradeExecution(success=False, error="Could not get current price")
            
            quantity = int(position_size / current_price)
            if quantity == 0:
                return TradeExecution(success=False, error="Position size too small")
            
            # Submit order
            order = self.api.submit_order(
                symbol=clean_symbol,
                qty=quantity,
                side='buy' if signal.side == OrderSide.BUY else 'sell',
                type='market',
                time_in_force='gtc'
            )
            
            # Create position
            position = Position(
                id=order.id,
                symbol=clean_symbol,
                side=signal.side,
                entry_price=current_price,
                quantity=quantity,
                stop_loss=signal.stop_loss,
                take_profit_levels=signal.take_profit_levels,
                status=PositionStatus.OPEN
            )
            
            logger.info(f"Trade executed: {position}")
            
            return TradeExecution(
                success=True,
                position=position,
                order_id=order.id,
                executed_price=current_price,
                executed_quantity=quantity
            )
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return TradeExecution(success=False, error=str(e))
    
    async def close_position(self, position: Position, percentage: float = 100.0) -> TradeExecution:
        try:
            quantity = int(position.quantity * (percentage / 100.0))
            
            order = self.api.submit_order(
                symbol=position.symbol,
                qty=quantity,
                side='sell' if position.side == OrderSide.BUY else 'buy',
                type='market',
                time_in_force='gtc'
            )
            
            current_price = await self.get_current_price(position.symbol)
            position.quantity -= quantity
            
            if position.quantity == 0:
                position.status = PositionStatus.CLOSED
            
            logger.info(f"Closed {percentage}% of position {position.id}")
            
            return TradeExecution(
                success=True,
                position=position,
                order_id=order.id,
                executed_price=current_price,
                executed_quantity=quantity
            )
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return TradeExecution(success=False, error=str(e))
    
    async def update_stop_loss(self, position: Position, new_stop_loss: float) -> bool:
        try:
            # Cancel existing stop loss orders
            orders = self.api.list_orders(status='open', symbols=position.symbol)
            for order in orders:
                if order.stop_price:
                    self.api.cancel_order(order.id)
            
            # Create new stop loss order
            self.api.submit_order(
                symbol=position.symbol,
                qty=position.quantity,
                side='sell' if position.side == OrderSide.BUY else 'buy',
                type='stop',
                time_in_force='gtc',
                stop_price=new_stop_loss
            )
            
            position.stop_loss = new_stop_loss
            logger.info(f"Stop loss updated to {new_stop_loss} for {position.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating stop loss: {e}")
            return False
    
    async def get_open_positions(self) -> List[Position]:
        try:
            positions = self.api.list_positions()
            result = []
            
            for pos in positions:
                result.append(Position(
                    id=pos.asset_id,
                    symbol=pos.symbol,
                    side=OrderSide.BUY if float(pos.qty) > 0 else OrderSide.SELL,
                    entry_price=float(pos.avg_entry_price),
                    quantity=abs(float(pos.qty)),
                    status=PositionStatus.OPEN,
                    pnl=float(pos.unrealized_pl)
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting open positions: {e}")
            return []


class BinanceBroker(BrokerInterface):
    """Binance broker implementation for crypto"""
    
    def __init__(self):
        try:
            from binance.client import Client
            self.client = Client(
                Config.BINANCE_API_KEY,
                Config.BINANCE_SECRET_KEY,
                testnet=Config.BINANCE_TESTNET
            )
            logger.info("Binance broker initialized")
        except ImportError:
            logger.error("python-binance not installed. Run: pip install python-binance")
            raise
    
    async def get_account_balance(self) -> float:
        try:
            account = self.client.get_account()
            # Sum USDT balance
            for balance in account['balances']:
                if balance['asset'] == 'USDT':
                    return float(balance['free']) + float(balance['locked'])
            return 0.0
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return 0.0
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    async def execute_trade(self, signal: TradingSignal, position_size: float) -> TradeExecution:
        try:
            current_price = await self.get_current_price(signal.symbol)
            if not current_price:
                return TradeExecution(success=False, error="Could not get current price")
            
            quantity = position_size / current_price
            
            # Round to proper precision
            quantity = round(quantity, 6)
            
            order = self.client.create_order(
                symbol=signal.symbol,
                side='BUY' if signal.side == OrderSide.BUY else 'SELL',
                type='MARKET',
                quantity=quantity
            )
            
            position = Position(
                id=str(order['orderId']),
                symbol=signal.symbol,
                side=signal.side,
                entry_price=current_price,
                quantity=quantity,
                stop_loss=signal.stop_loss,
                take_profit_levels=signal.take_profit_levels,
                status=PositionStatus.OPEN
            )
            
            logger.info(f"Trade executed: {position}")
            
            return TradeExecution(
                success=True,
                position=position,
                order_id=str(order['orderId']),
                executed_price=current_price,
                executed_quantity=quantity
            )
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return TradeExecution(success=False, error=str(e))
    
    async def close_position(self, position: Position, percentage: float = 100.0) -> TradeExecution:
        try:
            quantity = position.quantity * (percentage / 100.0)
            quantity = round(quantity, 6)
            
            order = self.client.create_order(
                symbol=position.symbol,
                side='SELL' if position.side == OrderSide.BUY else 'BUY',
                type='MARKET',
                quantity=quantity
            )
            
            current_price = await self.get_current_price(position.symbol)
            position.quantity -= quantity
            
            if position.quantity < 0.000001:
                position.status = PositionStatus.CLOSED
            
            logger.info(f"Closed {percentage}% of position {position.id}")
            
            return TradeExecution(
                success=True,
                position=position,
                order_id=str(order['orderId']),
                executed_price=current_price,
                executed_quantity=quantity
            )
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return TradeExecution(success=False, error=str(e))
    
    async def update_stop_loss(self, position: Position, new_stop_loss: float) -> bool:
        try:
            # Note: Binance requires OCO or stop-limit orders
            # This is a simplified implementation
            position.stop_loss = new_stop_loss
            logger.info(f"Stop loss updated to {new_stop_loss} for {position.symbol}")
            logger.warning("Note: Binance stop loss implementation is simplified")
            return True
            
        except Exception as e:
            logger.error(f"Error updating stop loss: {e}")
            return False
    
    async def get_open_positions(self) -> List[Position]:
        # Binance doesn't have a direct "positions" endpoint for spot trading
        # You would need to track positions manually or use futures API
        logger.warning("get_open_positions not fully implemented for Binance spot")
        return []


def get_broker() -> BrokerInterface:
    """Factory function to get the configured broker"""
    if Config.BROKER == "alpaca":
        return AlpacaBroker()
    elif Config.BROKER == "binance":
        return BinanceBroker()
    else:
        raise ValueError(f"Unsupported broker: {Config.BROKER}")
