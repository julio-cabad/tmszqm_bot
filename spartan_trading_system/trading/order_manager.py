"""
Order Manager - Spartan Trading System
Semi-automatic trading with order suggestions and risk management
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class OrderSuggestion:
    """Suggested order based on signal"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float
    stop_loss: float
    take_profit: float
    risk_amount: float
    potential_profit: float
    risk_reward_ratio: float
    confidence: float
    timestamp: datetime
    signal_type: str

class OrderManager:
    """
    Semi-Automatic Order Manager
    
    Generates order suggestions based on signals for manual confirmation
    """
    
    def __init__(self, config):
        """Initialize Order Manager"""
        self.config = config
        self.logger = logging.getLogger("OrderManager")
        
        # Trading parameters
        self.account_balance = 1000.0  # Default balance for testing
        self.max_risk_per_trade = 0.02  # 2% risk per trade
        self.risk_reward_ratio = 2.0  # 1:2 risk/reward
        
        # Order suggestions history
        self.order_suggestions: Dict[str, OrderSuggestion] = {}
        
        self.logger.info("🏛️ Spartan Order Manager initialized")
    
    def generate_order_suggestion(self, symbol: str, signal_type: str, 
                                current_price: float, tm_value: float, timeframe: str = "1m") -> Optional[OrderSuggestion]:
        """
        Generate order suggestion based on signal
        
        Args:
            symbol: Trading symbol
            signal_type: 'LONG' or 'SHORT'
            current_price: Current market price
            tm_value: Trend Magic value for stop loss reference
            timeframe: Trading timeframe for volatility adjustment
            
        Returns:
            OrderSuggestion or None
        """
        try:
            # Import position size from settings
            from config.settings import POSITION_SIZE
            position_value = POSITION_SIZE
            
            # Adjust stop loss distance based on timeframe volatility
            stop_loss_multiplier = self._get_stop_loss_multiplier(timeframe)
            
            if signal_type == 'LONG':
                # LONG position
                entry_price = current_price
                stop_loss = tm_value * (1 - stop_loss_multiplier)  # Adaptive stop loss
                take_profit = entry_price + (entry_price - stop_loss) * self.risk_reward_ratio
                
                # Calculate quantity for fixed $100 position
                quantity = position_value / entry_price
                
                side = OrderSide.BUY
                
            elif signal_type == 'SHORT':
                # SHORT position
                entry_price = current_price
                stop_loss = tm_value * (1 + stop_loss_multiplier)  # Adaptive stop loss
                take_profit = entry_price - (stop_loss - entry_price) * self.risk_reward_ratio
                
                # Calculate quantity for fixed $100 position
                quantity = position_value / entry_price
                
                side = OrderSide.SELL
                
            else:
                return None
            
            # Validate calculations
            if quantity <= 0:
                self.logger.warning(f"⚠️ Invalid quantity calculated for {symbol}: {quantity}")
                return None
            
            # Calculate potential profit and risk
            if signal_type == 'LONG':
                potential_profit = (take_profit - entry_price) * quantity
                risk_amount = (entry_price - stop_loss) * quantity
            else:
                potential_profit = (entry_price - take_profit) * quantity
                risk_amount = (stop_loss - entry_price) * quantity
            
            # Create order suggestion
            suggestion = OrderSuggestion(
                symbol=symbol,
                side=side,
                order_type=OrderType.MARKET,
                quantity=round(quantity, 6),
                price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_amount=risk_amount,
                potential_profit=potential_profit,
                risk_reward_ratio=self.risk_reward_ratio,
                confidence=0.8,  # Default confidence
                timestamp=datetime.now(),
                signal_type=signal_type
            )
            
            # Store suggestion
            self.order_suggestions[symbol] = suggestion
            
            self.logger.info(f"💡 Order suggestion generated for {symbol}: {signal_type}")
            return suggestion
            
        except Exception as e:
            self.logger.error(f"💀 Failed to generate order suggestion for {symbol}: {str(e)}")
            return None
    
    def format_order_suggestion(self, suggestion: OrderSuggestion) -> str:
        """Format order suggestion for display"""
        try:
            side_emoji = "🟢" if suggestion.side == OrderSide.BUY else "🔴"
            
            # Calculate stop loss distance percentage
            if suggestion.side == OrderSide.BUY:
                stop_distance = ((suggestion.price - suggestion.stop_loss) / suggestion.price) * 100
            else:
                stop_distance = ((suggestion.stop_loss - suggestion.price) / suggestion.price) * 100
            
            return (
                f"{side_emoji} {suggestion.symbol} {suggestion.signal_type} SUGGESTION\n"
                f"💰 Entry: ${suggestion.price:.4f}\n"
                f"🛑 Stop Loss: ${suggestion.stop_loss:.4f} ({stop_distance:.1f}%)\n"
                f"🎯 Take Profit: ${suggestion.take_profit:.4f}\n"
                f"📊 Quantity: {suggestion.quantity:.6f}\n"
                f"💰 Position Value: $100.00\n"
                f"⚠️ Risk: ${suggestion.risk_amount:.2f}\n"
                f"💵 Potential Profit: ${suggestion.potential_profit:.2f}\n"
                f"📈 R/R Ratio: 1:{suggestion.risk_reward_ratio}\n"
                f"⏰ Time: {suggestion.timestamp.strftime('%H:%M:%S')}"
            )
            
        except Exception as e:
            self.logger.error(f"💀 Failed to format order suggestion: {str(e)}")
            return f"Error formatting suggestion for {suggestion.symbol}"
    
    def get_active_suggestions(self) -> Dict[str, OrderSuggestion]:
        """Get all active order suggestions"""
        return self.order_suggestions.copy()
    
    def clear_suggestion(self, symbol: str) -> bool:
        """Clear order suggestion for symbol"""
        if symbol in self.order_suggestions:
            del self.order_suggestions[symbol]
            self.logger.info(f"🗑️ Cleared order suggestion for {symbol}")
            return True
        return False
    
    def update_account_balance(self, balance: float):
        """Update account balance for position sizing"""
        self.account_balance = balance
        self.logger.info(f"💰 Account balance updated: ${balance:.2f}")
    
    def set_risk_parameters(self, risk_per_trade: float, risk_reward_ratio: float):
        """Update risk management parameters"""
        self.max_risk_per_trade = risk_per_trade
        self.risk_reward_ratio = risk_reward_ratio
        self.logger.info(f"⚙️ Risk parameters updated: {risk_per_trade:.1%} risk, 1:{risk_reward_ratio} R/R")
    
    def _get_stop_loss_multiplier(self, timeframe: str) -> float:
        """
        Get stop loss multiplier based on timeframe volatility
        
        Args:
            timeframe: Trading timeframe
            
        Returns:
            Multiplier for stop loss distance (higher = wider stop)
        """
        # Stop loss multipliers based on timeframe volatility
        timeframe_multipliers = {
            '1m': 0.003,   # 0.3% - Very tight for scalping
            '3m': 0.005,   # 0.5% 
            '5m': 0.007,   # 0.7%
            '15m': 0.010,  # 1.0% - Standard
            '30m': 0.015,  # 1.5%
            '1h': 0.020,   # 2.0% - Wider for swing
            '2h': 0.025,   # 2.5%
            '4h': 0.030,   # 3.0%
            '6h': 0.035,   # 3.5%
            '12h': 0.040,  # 4.0%
            '1d': 0.050,   # 5.0% - Very wide for position
        }
        
        multiplier = timeframe_multipliers.get(timeframe, 0.010)  # Default 1.0%
        self.logger.debug(f"📊 Stop loss multiplier for {timeframe}: {multiplier:.1%}")
        return multiplier