"""
MetaTrader 5 Broker Integration
Handles connection and trading operations with MT5 platform
"""

import MetaTrader5 as mt5
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from config.models import Position, TradeExecution, OrderSide, PositionStatus
from brokers.broker_interface import BrokerInterface
from config.config import Config


class MT5Broker(BrokerInterface):
    """MetaTrader 5 broker implementation"""
    
    def __init__(self):
        self.connected = False
        self.account_info = None
        
    async def connect(self) -> bool:
        """Connect to MT5 terminal"""
        try:
            # Initialize MT5 connection
            if not mt5.initialize():
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            # Login to account
            account = int(Config.MT5_ACCOUNT)
            password = Config.MT5_PASSWORD
            server = Config.MT5_SERVER
            
            logger.info(f"Attempting to connect to MT5 account {account} on {server}")
            
            authorized = mt5.login(account, password=password, server=server)
            
            if not authorized:
                error = mt5.last_error()
                logger.error(f"MT5 login failed: {error}")
                mt5.shutdown()
                return False
            
            # Get account info
            self.account_info = mt5.account_info()
            if self.account_info is None:
                logger.error("Failed to get account info")
                mt5.shutdown()
                return False
            
            self.connected = True
            logger.info(f"✅ Connected to MT5 - Balance: ${self.account_info.balance:.2f}")
            logger.info(f"   Account: {account} | Server: {server}")
            logger.info(f"   Leverage: 1:{self.account_info.leverage}")
            
            return True
            
        except Exception as e:
            logger.exception(f"Error connecting to MT5: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from MT5"""
        try:
            if self.connected:
                mt5.shutdown()
                self.connected = False
                logger.info("Disconnected from MT5")
            return True
        except Exception as e:
            logger.exception(f"Error disconnecting from MT5: {e}")
            return False
    
    async def get_account_balance(self) -> float:
        """Get current account balance"""
        try:
            if not self.connected:
                logger.error("Not connected to MT5")
                return 0.0
            
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                return 0.0
            
            return float(account_info.balance)
            
        except Exception as e:
            logger.exception(f"Error getting account balance: {e}")
            return 0.0
    
    async def get_buying_power(self) -> float:
        """Get available buying power (free margin)"""
        try:
            if not self.connected:
                logger.error("Not connected to MT5")
                return 0.0
            
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                return 0.0
            
            # Free margin is the available buying power
            return float(account_info.margin_free)
            
        except Exception as e:
            logger.exception(f"Error getting buying power: {e}")
            return 0.0
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price for a symbol"""
        try:
            if not self.connected:
                logger.error("Not connected to MT5")
                return None
            
            # Normalize symbol for MT5 (e.g., EURUSD, GBPUSD, BTCUSD)
            mt5_symbol = self._normalize_symbol(symbol)
            
            # Get symbol tick
            tick = mt5.symbol_info_tick(mt5_symbol)
            if tick is None:
                logger.error(f"Failed to get tick for {mt5_symbol}")
                return None
            
            # Return bid price (for selling) or ask price (for buying)
            # Using bid as default current price
            return float(tick.bid)
            
        except Exception as e:
            logger.exception(f"Error getting current price for {symbol}: {e}")
            return None
    
    async def execute_trade(self, trade: TradeExecution) -> bool:
        """Execute a trade on MT5"""
        try:
            if not self.connected:
                logger.error("Not connected to MT5")
                return False
            
            symbol = self._normalize_symbol(trade.symbol)
            
            # Check if symbol exists and is tradeable
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Symbol {symbol} not found")
                return False
            
            if not symbol_info.visible:
                # Try to make symbol visible
                if not mt5.symbol_select(symbol, True):
                    logger.error(f"Failed to select symbol {symbol}")
                    return False
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"Failed to get tick for {symbol}")
                return False
            
            # Determine order type
            order_type = mt5.ORDER_TYPE_BUY if trade.side == OrderSide.BUY else mt5.ORDER_TYPE_SELL
            price = tick.ask if trade.side == OrderSide.BUY else tick.bid
            
            # Calculate lot size (volume)
            # MT5 uses lots, need to convert from quantity
            lot_size = self._calculate_lot_size(symbol, trade.quantity, price)
            
            # Prepare trade request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "deviation": 20,  # Maximum price deviation
                "magic": 234000,  # Magic number for our bot
                "comment": f"AI Agent - {trade.signal_type}",
                "type_time": mt5.ORDER_TIME_GTC,  # Good till cancelled
                "type_filling": mt5.ORDER_FILLING_IOC,  # Immediate or cancel
            }
            
            # Add stop loss if specified
            if trade.stop_loss:
                request["sl"] = trade.stop_loss
            
            # Add take profit if specified
            if trade.take_profit:
                request["tp"] = trade.take_profit
            
            # Send order
            logger.info(f"Sending MT5 order: {trade.side} {lot_size} lots of {symbol} @ {price}")
            result = mt5.order_send(request)
            
            if result is None:
                logger.error(f"Order send failed: {mt5.last_error()}")
                return False
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed with retcode: {result.retcode} - {result.comment}")
                return False
            
            logger.info(f"✅ Order executed successfully!")
            logger.info(f"   Order: {result.order} | Deal: {result.deal}")
            logger.info(f"   Price: {result.price} | Volume: {result.volume}")
            
            return True
            
        except Exception as e:
            logger.exception(f"Error executing trade: {e}")
            return False
    
    async def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        try:
            if not self.connected:
                logger.error("Not connected to MT5")
                return []
            
            positions = mt5.positions_get()
            if positions is None:
                return []
            
            result = []
            for pos in positions:
                position = Position(
                    symbol=self._denormalize_symbol(pos.symbol),
                    side=OrderSide.BUY if pos.type == mt5.ORDER_TYPE_BUY else OrderSide.SELL,
                    quantity=pos.volume,
                    entry_price=pos.price_open,
                    current_price=pos.price_current,
                    stop_loss=pos.sl if pos.sl != 0 else None,
                    take_profit=pos.tp if pos.tp != 0 else None,
                    status=PositionStatus.OPEN,
                    unrealized_pnl=pos.profit,
                    opened_at=datetime.fromtimestamp(pos.time)
                )
                position.position_id = str(pos.ticket)
                result.append(position)
            
            return result
            
        except Exception as e:
            logger.exception(f"Error getting open positions: {e}")
            return []
    
    async def close_position(self, position_id: str, percentage: float = 100.0) -> bool:
        """Close a position (full or partial)"""
        try:
            if not self.connected:
                logger.error("Not connected to MT5")
                return False
            
            # Get position by ticket
            positions = mt5.positions_get(ticket=int(position_id))
            if positions is None or len(positions) == 0:
                logger.error(f"Position {position_id} not found")
                return False
            
            position = positions[0]
            
            # Calculate volume to close
            volume_to_close = position.volume * (percentage / 100.0)
            
            # Determine close order type (opposite of position)
            close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            
            # Get current price
            tick = mt5.symbol_info_tick(position.symbol)
            if tick is None:
                logger.error(f"Failed to get tick for {position.symbol}")
                return False
            
            price = tick.bid if position.type == mt5.ORDER_TYPE_BUY else tick.ask
            
            # Prepare close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": volume_to_close,
                "type": close_type,
                "position": int(position_id),
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": f"AI Agent - Close {percentage}%",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send close order
            logger.info(f"Closing {percentage}% of position {position_id}")
            result = mt5.order_send(request)
            
            if result is None:
                logger.error(f"Close order failed: {mt5.last_error()}")
                return False
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Close order failed with retcode: {result.retcode} - {result.comment}")
                return False
            
            logger.info(f"✅ Position closed successfully - P&L: ${result.profit:.2f}")
            return True
            
        except Exception as e:
            logger.exception(f"Error closing position: {e}")
            return False
    
    async def update_stop_loss(self, position_id: str, new_stop_loss: float) -> bool:
        """Update stop loss for a position"""
        try:
            if not self.connected:
                logger.error("Not connected to MT5")
                return False
            
            # Get position
            positions = mt5.positions_get(ticket=int(position_id))
            if positions is None or len(positions) == 0:
                logger.error(f"Position {position_id} not found")
                return False
            
            position = positions[0]
            
            # Prepare modification request
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": int(position_id),
                "sl": new_stop_loss,
                "tp": position.tp,  # Keep existing take profit
                "magic": 234000,
                "comment": "AI Agent - Update SL"
            }
            
            # Send modification request
            logger.info(f"Updating stop loss for position {position_id} to {new_stop_loss}")
            result = mt5.order_send(request)
            
            if result is None:
                logger.error(f"SL update failed: {mt5.last_error()}")
                return False
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"SL update failed with retcode: {result.retcode} - {result.comment}")
                return False
            
            logger.info(f"✅ Stop loss updated successfully")
            return True
            
        except Exception as e:
            logger.exception(f"Error updating stop loss: {e}")
            return False
    
    def _normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol name for MT5
        Examples: BTCUSD -> BTCUSD, BTC/USD -> BTCUSD, EUR/USD -> EURUSD
        """
        # Remove slashes and spaces
        normalized = symbol.replace("/", "").replace(" ", "").upper()
        
        # Some common conversions
        conversions = {
            "XAUUSD": "GOLD",  # Gold
            "XAGUSD": "SILVER",  # Silver
            "US30": "US30",  # Dow Jones
            "NAS100": "NAS100",  # NASDAQ
            "SPX500": "SPX500",  # S&P 500
        }
        
        return conversions.get(normalized, normalized)
    
    def _denormalize_symbol(self, mt5_symbol: str) -> str:
        """Convert MT5 symbol back to standard format"""
        # Add slash for forex pairs
        if len(mt5_symbol) == 6 and mt5_symbol.isalpha():
            return f"{mt5_symbol[:3]}/{mt5_symbol[3:]}"
        return mt5_symbol
    
    def _calculate_lot_size(self, symbol: str, quantity: float, price: float) -> float:
        """
        Calculate lot size based on quantity and price
        For forex: 1 lot = 100,000 units
        For indices/commodities: varies by symbol
        """
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.warning(f"Could not get symbol info for {symbol}, using default lot calculation")
            return 0.01  # Minimum lot size
        
        # Get contract size (lot size)
        contract_size = symbol_info.trade_contract_size
        
        # Calculate lots needed
        # quantity is in USD value, convert to lots
        lot_size = quantity / (price * contract_size)
        
        # Round to symbol's volume step
        volume_step = symbol_info.volume_step
        lot_size = round(lot_size / volume_step) * volume_step
        
        # Ensure within min/max limits
        lot_size = max(symbol_info.volume_min, min(lot_size, symbol_info.volume_max))
        
        return lot_size
