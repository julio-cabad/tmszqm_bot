"""
Position Calculator - Spartan Risk Management
Calculates position sizes, stop losses, and take profits with precision
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple
import math

from ..config.strategy_config import StrategyConfig
from .risk_models import (
    PositionSize, StopLoss, TakeProfit, Direction, RiskLevel
)


class PositionCalculator:
    """
    Spartan Position Calculator
    
    Calculates optimal position sizes, stop losses, and take profits
    based on account balance, risk parameters, and market conditions.
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize Position Calculator
        
        Args:
            config: StrategyConfig with risk parameters
        """
        self.config = config
        self.logger = logging.getLogger("PositionCalculator")
        
        self.logger.info(f"🏛️ Spartan Position Calculator initialized")
        self.logger.info(f"⚔️ Risk Percentage: {config.risk_percentage}%")
        self.logger.info(f"🛡️ Max Positions: {config.max_positions}")
    
    def calculate_position_size(
        self, 
        symbol: str,
        direction: Direction,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        leverage: float = 1.0
    ) -> PositionSize:
        """
        Calculate optimal position size based on risk parameters
        
        Args:
            symbol: Trading pair
            direction: LONG or SHORT
            account_balance: Current account balance
            entry_price: Planned entry price
            stop_loss_price: Stop loss price
            leverage: Leverage multiplier (default 1.0)
            
        Returns:
            PositionSize with all calculations
        """
        try:
            # Calculate risk amount (dollar amount willing to lose)
            risk_amount = account_balance * (self.config.risk_percentage / 100)
            
            # Calculate price difference (risk per unit)
            if direction == Direction.LONG:
                price_diff = abs(entry_price - stop_loss_price)
            else:  # SHORT
                price_diff = abs(stop_loss_price - entry_price)
            
            if price_diff <= 0:
                raise ValueError(f"Invalid price difference: entry={entry_price}, stop={stop_loss_price}")
            
            # Calculate position size in base currency
            position_size_base = risk_amount / price_diff
            
            # Calculate position size in USD
            position_size_usd = position_size_base * entry_price
            
            # Apply leverage
            if leverage > 1.0:
                position_size_usd *= leverage
                position_size_base *= leverage
            
            # Calculate risk-reward ratio (will be updated with take profit)
            risk_reward_ratio = 1.0  # Default, will be calculated with TP
            
            # Calculate max loss percentage
            max_loss_percentage = (risk_amount / account_balance) * 100
            
            result = PositionSize(
                symbol=symbol,
                direction=direction,
                account_balance=account_balance,
                risk_percentage=self.config.risk_percentage,
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                risk_amount=risk_amount,
                position_size_usd=position_size_usd,
                position_size_base=position_size_base,
                leverage_used=leverage,
                risk_reward_ratio=risk_reward_ratio,
                max_loss_percentage=max_loss_percentage,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"📊 Position size calculated for {symbol}: ${position_size_usd:,.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"💀 Position size calculation failed: {str(e)}")
            raise
    
    def calculate_stop_loss(
        self,
        symbol: str,
        direction: Direction,
        entry_price: float,
        trend_magic_value: float,
        atr_value: float
    ) -> StopLoss:
        """
        Calculate multiple stop loss levels and recommend the best one
        
        Args:
            symbol: Trading pair
            direction: LONG or SHORT
            entry_price: Entry price
            trend_magic_value: Current Trend Magic line value
            atr_value: Current ATR value
            
        Returns:
            StopLoss with multiple levels and recommendation
        """
        try:
            # 1. Trend Magic Stop (primary method)
            if direction == Direction.LONG:
                trend_magic_stop = trend_magic_value * 0.995  # Slightly below TM line
            else:  # SHORT
                trend_magic_stop = trend_magic_value * 1.005  # Slightly above TM line
            
            # 2. ATR-based Stop
            atr_multiplier = 2.0  # Conservative ATR multiplier
            if direction == Direction.LONG:
                atr_stop = entry_price - (atr_value * atr_multiplier)
            else:  # SHORT
                atr_stop = entry_price + (atr_value * atr_multiplier)
            
            # 3. Percentage-based Stop
            percentage_stop_distance = 0.02  # 2% default
            if direction == Direction.LONG:
                percentage_stop = entry_price * (1 - percentage_stop_distance)
            else:  # SHORT
                percentage_stop = entry_price * (1 + percentage_stop_distance)
            
            # Choose the best stop loss (most conservative for risk management)
            stops = {
                'trend_magic': trend_magic_stop,
                'atr': atr_stop,
                'percentage': percentage_stop
            }
            
            if direction == Direction.LONG:
                # For LONG, choose the highest stop (least risk)
                recommended_stop = max(stops.values())
                stop_type = max(stops, key=stops.get)
            else:  # SHORT
                # For SHORT, choose the lowest stop (least risk)
                recommended_stop = min(stops.values())
                stop_type = min(stops, key=stops.get)
            
            # Calculate stop distance metrics
            stop_distance_pips = abs(entry_price - recommended_stop)
            stop_distance_percentage = (stop_distance_pips / entry_price) * 100
            
            result = StopLoss(
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                trend_magic_stop=trend_magic_stop,
                atr_stop=atr_stop,
                percentage_stop=percentage_stop,
                recommended_stop=recommended_stop,
                stop_type=stop_type,
                stop_distance_pips=stop_distance_pips,
                stop_distance_percentage=stop_distance_percentage,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"🛡️ Stop loss calculated for {symbol}: ${recommended_stop:,.4f} ({stop_type})")
            return result
            
        except Exception as e:
            self.logger.error(f"💀 Stop loss calculation failed: {str(e)}")
            raise
    
    def calculate_take_profit(
        self,
        symbol: str,
        direction: Direction,
        entry_price: float,
        stop_loss_price: float
    ) -> TakeProfit:
        """
        Calculate multiple take profit levels with risk-reward ratios
        
        Args:
            symbol: Trading pair
            direction: LONG or SHORT
            entry_price: Entry price
            stop_loss_price: Stop loss price
            
        Returns:
            TakeProfit with multiple levels
        """
        try:
            # Calculate risk (distance to stop loss)
            if direction == Direction.LONG:
                risk_distance = entry_price - stop_loss_price
            else:  # SHORT
                risk_distance = stop_loss_price - entry_price
            
            if risk_distance <= 0:
                raise ValueError(f"Invalid risk distance: {risk_distance}")
            
            # Calculate take profit levels
            if direction == Direction.LONG:
                tp1_price = entry_price + (risk_distance * 1.0)  # 1:1 R:R
                tp2_price = entry_price + (risk_distance * 2.0)  # 1:2 R:R
                tp3_price = entry_price + (risk_distance * 3.0)  # 1:3 R:R
            else:  # SHORT
                tp1_price = entry_price - (risk_distance * 1.0)  # 1:1 R:R
                tp2_price = entry_price - (risk_distance * 2.0)  # 1:2 R:R
                tp3_price = entry_price - (risk_distance * 3.0)  # 1:3 R:R
            
            # Risk-reward ratios
            tp1_rr_ratio = 1.0
            tp2_rr_ratio = 2.0
            tp3_rr_ratio = 3.0
            
            # Position allocation percentages (Spartan strategy)
            tp1_allocation = 0.50  # Close 50% at TP1 (secure profits)
            tp2_allocation = 0.30  # Close 30% at TP2 (good profits)
            tp3_allocation = 0.20  # Close 20% at TP3 (let winners run)
            
            result = TakeProfit(
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                tp1_price=tp1_price,
                tp2_price=tp2_price,
                tp3_price=tp3_price,
                tp1_rr_ratio=tp1_rr_ratio,
                tp2_rr_ratio=tp2_rr_ratio,
                tp3_rr_ratio=tp3_rr_ratio,
                tp1_allocation=tp1_allocation,
                tp2_allocation=tp2_allocation,
                tp3_allocation=tp3_allocation,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"🎯 Take profits calculated for {symbol}: TP1=${tp1_price:,.4f}, TP2=${tp2_price:,.4f}, TP3=${tp3_price:,.4f}")
            return result
            
        except Exception as e:
            self.logger.error(f"💀 Take profit calculation failed: {str(e)}")
            raise
    
    def validate_position_size(self, position_size: PositionSize) -> Tuple[bool, List[str]]:
        """
        Validate position size against risk parameters
        
        Args:
            position_size: PositionSize to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            # Check if position size exceeds account balance
            if position_size.position_size_usd > position_size.account_balance:
                errors.append(f"Position size (${position_size.position_size_usd:,.2f}) exceeds account balance (${position_size.account_balance:,.2f})")
            
            # Check if risk percentage is within limits
            if position_size.risk_percentage > 10.0:
                errors.append(f"Risk percentage ({position_size.risk_percentage}%) exceeds maximum (10%)")
            
            # Check if risk amount is reasonable
            max_risk_amount = position_size.account_balance * 0.05  # 5% max
            if position_size.risk_amount > max_risk_amount:
                errors.append(f"Risk amount (${position_size.risk_amount:,.2f}) exceeds 5% of account balance")
            
            # Check leverage limits
            if position_size.leverage_used > 10.0:
                errors.append(f"Leverage ({position_size.leverage_used}x) exceeds maximum (10x)")
            
            # Check minimum position size
            min_position_size = 10.0  # $10 minimum
            if position_size.position_size_usd < min_position_size:
                errors.append(f"Position size (${position_size.position_size_usd:,.2f}) below minimum (${min_position_size})")
            
            is_valid = len(errors) == 0
            
            if is_valid:
                self.logger.info(f"✅ Position size validation passed for {position_size.symbol}")
            else:
                self.logger.warning(f"⚠️ Position size validation failed for {position_size.symbol}: {len(errors)} errors")
            
            return is_valid, errors
            
        except Exception as e:
            self.logger.error(f"💀 Position size validation failed: {str(e)}")
            return False, [f"Validation error: {str(e)}"]
    
    def calculate_risk_reward_ratio(self, entry_price: float, stop_loss_price: float, take_profit_price: float, direction: Direction) -> float:
        """
        Calculate risk-reward ratio for a trade
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            take_profit_price: Take profit price
            direction: LONG or SHORT
            
        Returns:
            Risk-reward ratio
        """
        try:
            if direction == Direction.LONG:
                risk = entry_price - stop_loss_price
                reward = take_profit_price - entry_price
            else:  # SHORT
                risk = stop_loss_price - entry_price
                reward = entry_price - take_profit_price
            
            if risk <= 0:
                return 0.0
            
            rr_ratio = reward / risk
            return max(0.0, rr_ratio)
            
        except Exception as e:
            self.logger.error(f"💀 Risk-reward calculation failed: {str(e)}")
            return 0.0
    
    def get_position_summary(self, position_size: PositionSize, stop_loss: StopLoss, take_profit: TakeProfit) -> Dict[str, Any]:
        """
        Get comprehensive position summary
        
        Args:
            position_size: Position size calculation
            stop_loss: Stop loss calculation
            take_profit: Take profit calculation
            
        Returns:
            Dictionary with position summary
        """
        try:
            # Calculate final risk-reward ratio with TP2 as primary target
            final_rr_ratio = self.calculate_risk_reward_ratio(
                position_size.entry_price,
                stop_loss.recommended_stop,
                take_profit.tp2_price,
                position_size.direction
            )
            
            return {
                'symbol': position_size.symbol,
                'direction': position_size.direction.value,
                'entry_price': position_size.entry_price,
                'stop_loss': stop_loss.recommended_stop,
                'stop_type': stop_loss.stop_type,
                'take_profit_1': take_profit.tp1_price,
                'take_profit_2': take_profit.tp2_price,
                'take_profit_3': take_profit.tp3_price,
                'position_size_usd': position_size.position_size_usd,
                'position_size_base': position_size.position_size_base,
                'risk_amount': position_size.risk_amount,
                'risk_percentage': position_size.risk_percentage,
                'risk_reward_ratio': final_rr_ratio,
                'leverage': position_size.leverage_used,
                'stop_distance_pct': stop_loss.stop_distance_percentage,
                'tp_allocations': {
                    'tp1': take_profit.tp1_allocation,
                    'tp2': take_profit.tp2_allocation,
                    'tp3': take_profit.tp3_allocation
                }
            }
            
        except Exception as e:
            self.logger.error(f"💀 Position summary failed: {str(e)}")
            return {}