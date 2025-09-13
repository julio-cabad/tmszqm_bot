"""
Risk Manager - Spartan Risk Management System
Comprehensive risk management with portfolio-level controls
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import json

from ..config.strategy_config import StrategyConfig
from ..strategy.signal_types import TradingSignal
from .position_calculator import PositionCalculator
from .risk_models import (
    RiskAssessment, PortfolioRisk, RiskLevel, Direction,
    PositionSize, StopLoss, TakeProfit
)


class RiskManagementError(Exception):
    """Risk management related errors"""
    pass


class RiskManager:
    """
    Spartan Risk Manager
    
    Provides comprehensive risk management including:
    - Position sizing based on account balance and risk tolerance
    - Stop loss calculation using multiple methods
    - Take profit levels with optimal risk-reward ratios
    - Portfolio-level risk monitoring
    - Risk validation and limits enforcement
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize Risk Manager
        
        Args:
            config: StrategyConfig with risk parameters
        """
        self.config = config
        self.logger = logging.getLogger("RiskManager")
        
        # Initialize position calculator
        self.position_calculator = PositionCalculator(config)
        
        # Portfolio tracking
        self.active_positions: Dict[str, Dict[str, Any]] = {}
        self.risk_history: List[Dict[str, Any]] = []
        
        # Risk limits
        self.daily_risk_limit = config.risk_percentage * 3  # 3x daily risk
        self.weekly_risk_limit = config.risk_percentage * 10  # 10x weekly risk
        self.monthly_risk_limit = config.risk_percentage * 20  # 20x monthly risk
        
        self.logger.info(f"🏛️ Spartan Risk Manager initialized")
        self.logger.info(f"⚔️ Risk per trade: {config.risk_percentage}%")
        self.logger.info(f"🛡️ Max positions: {config.max_positions}")
        self.logger.info(f"📊 Daily risk limit: {self.daily_risk_limit}%")
    
    def assess_signal_risk(
        self,
        signal: TradingSignal,
        account_balance: float,
        trend_magic_value: float,
        atr_value: float
    ) -> RiskAssessment:
        """
        Comprehensive risk assessment for a trading signal
        
        Args:
            signal: TradingSignal to assess
            account_balance: Current account balance
            trend_magic_value: Current Trend Magic line value
            atr_value: Current ATR value
            
        Returns:
            RiskAssessment with complete risk analysis
        """
        try:
            self.logger.info(f"🎯 Assessing risk for {signal.symbol} {signal.direction.value} signal")
            
            # Convert signal direction to risk model direction
            from .risk_models import Direction as RiskDirection
            direction = RiskDirection.LONG if signal.direction.value == "long" else RiskDirection.SHORT
            
            # Calculate stop loss first
            stop_loss = self.position_calculator.calculate_stop_loss(
                symbol=signal.symbol,
                direction=direction,
                entry_price=signal.entry_price,
                trend_magic_value=trend_magic_value,
                atr_value=atr_value
            )
            
            # Calculate position size
            position_size = self.position_calculator.calculate_position_size(
                symbol=signal.symbol,
                direction=direction,
                account_balance=account_balance,
                entry_price=signal.entry_price,
                stop_loss_price=stop_loss.recommended_stop
            )
            
            # Calculate take profit levels
            take_profit = self.position_calculator.calculate_take_profit(
                symbol=signal.symbol,
                direction=direction,
                entry_price=signal.entry_price,
                stop_loss_price=stop_loss.recommended_stop
            )
            
            # Update position size with final R:R ratio
            position_size.risk_reward_ratio = self.position_calculator.calculate_risk_reward_ratio(
                signal.entry_price,
                stop_loss.recommended_stop,
                take_profit.tp2_price,  # Use TP2 as primary target
                direction
            )
            
            # Validate position
            is_valid, validation_errors = self.position_calculator.validate_position_size(position_size)
            validation_warnings = []
            
            # Additional risk validations
            additional_errors, additional_warnings = self._validate_signal_risk(signal, position_size, account_balance)
            validation_errors.extend(additional_errors)
            validation_warnings.extend(additional_warnings)
            
            # Calculate risk score and level
            risk_score = self._calculate_risk_score(signal, position_size, stop_loss)
            risk_level = self._determine_risk_level(risk_score)
            
            # Assess market conditions
            volatility_assessment = self._assess_volatility(atr_value, signal.symbol)
            liquidity_assessment = self._assess_liquidity(signal.symbol)
            
            # Calculate portfolio impact
            portfolio_risk_pct = self._calculate_portfolio_risk_percentage(position_size.risk_amount, account_balance)
            correlation_risk = self._calculate_correlation_risk(signal.symbol)
            
            # Final validation
            if validation_errors:
                is_valid = False
            
            risk_assessment = RiskAssessment(
                symbol=signal.symbol,
                direction=direction,
                signal_strength=signal.strength,
                position_size=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_level=risk_level,
                risk_score=risk_score,
                is_valid=is_valid,
                validation_errors=validation_errors,
                validation_warnings=validation_warnings,
                volatility_assessment=volatility_assessment,
                liquidity_assessment=liquidity_assessment,
                portfolio_risk_percentage=portfolio_risk_pct,
                correlation_risk=correlation_risk,
                timestamp=datetime.now()
            )
            
            # Log assessment result
            if is_valid:
                self.logger.info(f"✅ Risk assessment passed for {signal.symbol}: {risk_level.value} risk, ${position_size.position_size_usd:,.2f} position")
            else:
                self.logger.warning(f"❌ Risk assessment failed for {signal.symbol}: {len(validation_errors)} errors")
            
            return risk_assessment
            
        except Exception as e:
            self.logger.error(f"💀 Risk assessment failed for {signal.symbol}: {str(e)}")
            raise RiskManagementError(f"Risk assessment failed: {str(e)}")
    
    def _validate_signal_risk(self, signal: TradingSignal, position_size: PositionSize, account_balance: float) -> Tuple[List[str], List[str]]:
        """
        Additional signal-specific risk validations
        
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        try:
            # Check signal strength
            if signal.strength < self.config.min_signal_strength:
                errors.append(f"Signal strength ({signal.strength:.2f}) below minimum ({self.config.min_signal_strength})")
            
            # Check if we already have a position in this symbol
            if signal.symbol in self.active_positions:
                if self.config.max_positions_per_symbol <= 1:
                    errors.append(f"Already have active position in {signal.symbol}")
                else:
                    warnings.append(f"Adding to existing position in {signal.symbol}")
            
            # Check maximum positions limit
            if len(self.active_positions) >= self.config.max_positions:
                errors.append(f"Maximum positions ({self.config.max_positions}) already reached")
            
            # Check portfolio risk concentration
            if position_size.risk_amount > account_balance * 0.05:  # 5% max per trade
                warnings.append(f"High risk concentration: {(position_size.risk_amount/account_balance)*100:.1f}% of account")
            
            # Check if position size is too small to be meaningful
            if position_size.position_size_usd < 50:  # $50 minimum
                warnings.append(f"Small position size: ${position_size.position_size_usd:.2f}")
            
            return errors, warnings
            
        except Exception as e:
            self.logger.error(f"💀 Signal validation failed: {str(e)}")
            return [f"Validation error: {str(e)}"], []
    
    def _calculate_risk_score(self, signal: TradingSignal, position_size: PositionSize, stop_loss: StopLoss) -> float:
        """
        Calculate overall risk score (0.0 to 1.0)
        
        Returns:
            Risk score where 0.0 is lowest risk, 1.0 is highest risk
        """
        try:
            risk_factors = []
            
            # Signal strength factor (lower strength = higher risk)
            signal_risk = 1.0 - signal.strength
            risk_factors.append(signal_risk * 0.3)  # 30% weight
            
            # Position size factor (larger position = higher risk)
            position_risk = min(position_size.position_size_usd / position_size.account_balance, 0.5) * 2
            risk_factors.append(position_risk * 0.2)  # 20% weight
            
            # Stop distance factor (wider stop = higher risk)
            stop_risk = min(stop_loss.stop_distance_percentage / 5.0, 1.0)  # 5% stop = max risk
            risk_factors.append(stop_risk * 0.3)  # 30% weight
            
            # Risk-reward factor (lower R:R = higher risk)
            rr_risk = max(0.0, 1.0 - (position_size.risk_reward_ratio / 3.0))  # 3:1 R:R = low risk
            risk_factors.append(rr_risk * 0.2)  # 20% weight
            
            # Calculate weighted average
            total_risk = sum(risk_factors)
            return min(1.0, max(0.0, total_risk))
            
        except Exception as e:
            self.logger.error(f"💀 Risk score calculation failed: {str(e)}")
            return 0.5  # Default medium risk
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """
        Determine risk level based on risk score
        
        Args:
            risk_score: Risk score (0.0 to 1.0)
            
        Returns:
            RiskLevel classification
        """
        if risk_score <= 0.25:
            return RiskLevel.LOW
        elif risk_score <= 0.5:
            return RiskLevel.MEDIUM
        elif risk_score <= 0.75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.EXTREME
    
    def _assess_volatility(self, atr_value: float, symbol: str) -> str:
        """
        Assess market volatility based on ATR
        
        Args:
            atr_value: Current ATR value
            symbol: Trading symbol
            
        Returns:
            Volatility assessment string
        """
        try:
            # Simple volatility assessment based on ATR
            # This could be enhanced with historical ATR comparison
            if atr_value > 1000:  # High ATR for major pairs
                return "HIGH"
            elif atr_value > 500:
                return "MEDIUM"
            else:
                return "LOW"
                
        except Exception:
            return "UNKNOWN"
    
    def _assess_liquidity(self, symbol: str) -> str:
        """
        Assess market liquidity for the symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Liquidity assessment string
        """
        try:
            # Major pairs have high liquidity
            major_pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]
            
            if symbol in major_pairs:
                return "HIGH"
            elif symbol.endswith("USDT"):
                return "MEDIUM"
            else:
                return "LOW"
                
        except Exception:
            return "UNKNOWN"
    
    def _calculate_portfolio_risk_percentage(self, risk_amount: float, account_balance: float) -> float:
        """
        Calculate what percentage of portfolio this risk represents
        
        Args:
            risk_amount: Dollar amount at risk
            account_balance: Total account balance
            
        Returns:
            Portfolio risk percentage
        """
        try:
            return (risk_amount / account_balance) * 100
        except Exception:
            return 0.0
    
    def _calculate_correlation_risk(self, symbol: str) -> float:
        """
        Calculate correlation risk with existing positions
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Correlation risk score (0.0 to 1.0)
        """
        try:
            # Simple correlation assessment
            # This could be enhanced with actual correlation calculations
            
            if not self.active_positions:
                return 0.0  # No correlation risk if no positions
            
            # Check for similar assets
            base_asset = symbol.replace("USDT", "")
            correlation_count = 0
            
            for active_symbol in self.active_positions.keys():
                active_base = active_symbol.replace("USDT", "")
                
                # High correlation pairs
                if base_asset == active_base:
                    correlation_count += 1.0  # Same asset
                elif (base_asset in ["BTC", "ETH"] and active_base in ["BTC", "ETH"]):
                    correlation_count += 0.7  # Major crypto correlation
                elif symbol.endswith("USDT") and active_symbol.endswith("USDT"):
                    correlation_count += 0.3  # General crypto correlation
            
            # Normalize correlation risk
            max_correlation = len(self.active_positions)
            return min(1.0, correlation_count / max_correlation) if max_correlation > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"💀 Correlation risk calculation failed: {str(e)}")
            return 0.5  # Default medium correlation
    
    def add_position(self, risk_assessment: RiskAssessment) -> bool:
        """
        Add a position to portfolio tracking
        
        Args:
            risk_assessment: Validated risk assessment
            
        Returns:
            True if position added successfully
        """
        try:
            if not risk_assessment.is_valid:
                self.logger.warning(f"⚠️ Cannot add invalid position for {risk_assessment.symbol}")
                return False
            
            position_data = {
                'symbol': risk_assessment.symbol,
                'direction': risk_assessment.direction.value,
                'entry_price': risk_assessment.position_size.entry_price,
                'position_size': risk_assessment.position_size.position_size_usd,
                'risk_amount': risk_assessment.position_size.risk_amount,
                'stop_loss': risk_assessment.stop_loss.recommended_stop,
                'take_profit_1': risk_assessment.take_profit.tp1_price,
                'take_profit_2': risk_assessment.take_profit.tp2_price,
                'take_profit_3': risk_assessment.take_profit.tp3_price,
                'risk_level': risk_assessment.risk_level.value,
                'timestamp': datetime.now().isoformat()
            }
            
            self.active_positions[risk_assessment.symbol] = position_data
            
            # Add to risk history
            self.risk_history.append({
                'action': 'ADD_POSITION',
                'symbol': risk_assessment.symbol,
                'risk_amount': risk_assessment.position_size.risk_amount,
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"✅ Position added to portfolio: {risk_assessment.symbol} (${risk_assessment.position_size.position_size_usd:,.2f})")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to add position: {str(e)}")
            return False
    
    def remove_position(self, symbol: str) -> bool:
        """
        Remove a position from portfolio tracking
        
        Args:
            symbol: Symbol to remove
            
        Returns:
            True if position removed successfully
        """
        try:
            if symbol not in self.active_positions:
                self.logger.warning(f"⚠️ Position {symbol} not found in portfolio")
                return False
            
            position_data = self.active_positions.pop(symbol)
            
            # Add to risk history
            self.risk_history.append({
                'action': 'REMOVE_POSITION',
                'symbol': symbol,
                'risk_amount': position_data.get('risk_amount', 0),
                'timestamp': datetime.now().isoformat()
            })
            
            self.logger.info(f"✅ Position removed from portfolio: {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"💀 Failed to remove position: {str(e)}")
            return False
    
    def get_portfolio_risk(self, account_balance: float) -> PortfolioRisk:
        """
        Get comprehensive portfolio risk assessment
        
        Args:
            account_balance: Current account balance
            
        Returns:
            PortfolioRisk with complete portfolio analysis
        """
        try:
            # Calculate total risk
            total_risk_amount = sum(pos.get('risk_amount', 0) for pos in self.active_positions.values())
            total_risk_percentage = (total_risk_amount / account_balance) * 100 if account_balance > 0 else 0
            
            # Risk per symbol
            risk_per_symbol = {
                symbol: pos.get('risk_amount', 0) 
                for symbol, pos in self.active_positions.items()
            }
            
            # Simple correlation matrix (could be enhanced)
            correlation_matrix = self._build_correlation_matrix()
            
            # Determine portfolio risk level
            if total_risk_percentage <= 5:
                portfolio_risk_level = RiskLevel.LOW
            elif total_risk_percentage <= 10:
                portfolio_risk_level = RiskLevel.MEDIUM
            elif total_risk_percentage <= 20:
                portfolio_risk_level = RiskLevel.HIGH
            else:
                portfolio_risk_level = RiskLevel.EXTREME
            
            # Check if we can take new positions
            can_take_new = (
                len(self.active_positions) < self.config.max_positions and
                total_risk_percentage < self.daily_risk_limit
            )
            
            # Recommended position size multiplier
            if total_risk_percentage > 15:
                multiplier = 0.5  # Reduce position sizes
            elif total_risk_percentage > 10:
                multiplier = 0.75  # Slightly reduce
            else:
                multiplier = 1.0  # Normal sizing
            
            portfolio_risk = PortfolioRisk(
                total_account_balance=account_balance,
                total_risk_amount=total_risk_amount,
                total_risk_percentage=total_risk_percentage,
                active_positions=len(self.active_positions),
                max_positions=self.config.max_positions,
                risk_per_symbol=risk_per_symbol,
                correlation_matrix=correlation_matrix,
                daily_risk_limit=self.daily_risk_limit,
                weekly_risk_limit=self.weekly_risk_limit,
                monthly_risk_limit=self.monthly_risk_limit,
                risk_level=portfolio_risk_level,
                can_take_new_position=can_take_new,
                recommended_position_size_multiplier=multiplier,
                timestamp=datetime.now()
            )
            
            return portfolio_risk
            
        except Exception as e:
            self.logger.error(f"💀 Portfolio risk calculation failed: {str(e)}")
            raise RiskManagementError(f"Portfolio risk calculation failed: {str(e)}")
    
    def _build_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Build simple correlation matrix for active positions
        
        Returns:
            Correlation matrix dictionary
        """
        try:
            symbols = list(self.active_positions.keys())
            matrix = {}
            
            for symbol1 in symbols:
                matrix[symbol1] = {}
                for symbol2 in symbols:
                    if symbol1 == symbol2:
                        matrix[symbol1][symbol2] = 1.0
                    else:
                        # Simple correlation estimation
                        base1 = symbol1.replace("USDT", "")
                        base2 = symbol2.replace("USDT", "")
                        
                        if base1 == base2:
                            correlation = 1.0
                        elif (base1 in ["BTC", "ETH"] and base2 in ["BTC", "ETH"]):
                            correlation = 0.7
                        else:
                            correlation = 0.3  # General crypto correlation
                        
                        matrix[symbol1][symbol2] = correlation
            
            return matrix
            
        except Exception as e:
            self.logger.error(f"💀 Correlation matrix build failed: {str(e)}")
            return {}
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """
        Get summary of current risk management status
        
        Returns:
            Dictionary with risk summary
        """
        try:
            return {
                'active_positions': len(self.active_positions),
                'max_positions': self.config.max_positions,
                'risk_per_trade': self.config.risk_percentage,
                'daily_risk_limit': self.daily_risk_limit,
                'positions': list(self.active_positions.keys()),
                'risk_history_entries': len(self.risk_history)
            }
            
        except Exception as e:
            self.logger.error(f"💀 Risk summary failed: {str(e)}")
            return {}