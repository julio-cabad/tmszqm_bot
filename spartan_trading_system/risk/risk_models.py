"""
Risk Management Data Models
Standardized models for risk calculations and assessments
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class Direction(Enum):
    """Trading direction"""
    LONG = "LONG"
    SHORT = "SHORT"


class RiskLevel(Enum):
    """Risk level classification"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


@dataclass
class PositionSize:
    """Position size calculation result"""
    symbol: str
    direction: Direction
    account_balance: float
    risk_percentage: float
    entry_price: float
    stop_loss_price: float
    
    # Calculated values
    risk_amount: float  # Dollar amount at risk
    position_size_usd: float  # Position size in USD
    position_size_base: float  # Position size in base currency
    leverage_used: float  # Leverage multiplier
    
    # Risk metrics
    risk_reward_ratio: float
    max_loss_percentage: float
    
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        return {
            'symbol': self.symbol,
            'direction': self.direction.value,
            'account_balance': self.account_balance,
            'risk_percentage': self.risk_percentage,
            'entry_price': self.entry_price,
            'stop_loss_price': self.stop_loss_price,
            'risk_amount': self.risk_amount,
            'position_size_usd': self.position_size_usd,
            'position_size_base': self.position_size_base,
            'leverage_used': self.leverage_used,
            'risk_reward_ratio': self.risk_reward_ratio,
            'max_loss_percentage': self.max_loss_percentage,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class StopLoss:
    """Stop loss calculation result"""
    symbol: str
    direction: Direction
    entry_price: float
    
    # Stop loss levels
    trend_magic_stop: float  # Based on Trend Magic line
    atr_stop: float  # Based on ATR calculation
    percentage_stop: float  # Based on percentage
    
    # Recommended stop
    recommended_stop: float
    stop_type: str  # Type of recommended stop
    
    # Risk metrics
    stop_distance_pips: float
    stop_distance_percentage: float
    
    timestamp: datetime


@dataclass
class TakeProfit:
    """Take profit levels calculation"""
    symbol: str
    direction: Direction
    entry_price: float
    stop_loss_price: float
    
    # Multiple take profit levels
    tp1_price: float  # Conservative target (1:1 R:R)
    tp2_price: float  # Moderate target (1:2 R:R)
    tp3_price: float  # Aggressive target (1:3 R:R)
    
    # Risk-reward ratios
    tp1_rr_ratio: float
    tp2_rr_ratio: float
    tp3_rr_ratio: float
    
    # Percentage allocations
    tp1_allocation: float  # Percentage of position to close at TP1
    tp2_allocation: float  # Percentage of position to close at TP2
    tp3_allocation: float  # Percentage of position to close at TP3
    
    timestamp: datetime


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment for a trading signal"""
    symbol: str
    direction: Direction
    signal_strength: float
    
    # Position sizing
    position_size: PositionSize
    
    # Risk management
    stop_loss: StopLoss
    take_profit: TakeProfit
    
    # Risk classification
    risk_level: RiskLevel
    risk_score: float  # 0.0 to 1.0
    
    # Validation results
    is_valid: bool
    validation_errors: List[str]
    validation_warnings: List[str]
    
    # Market conditions
    volatility_assessment: str
    liquidity_assessment: str
    
    # Portfolio impact
    portfolio_risk_percentage: float
    correlation_risk: float
    
    timestamp: datetime
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get summary of risk assessment"""
        return {
            'symbol': self.symbol,
            'direction': self.direction.value,
            'risk_level': self.risk_level.value,
            'risk_score': self.risk_score,
            'position_size_usd': self.position_size.position_size_usd,
            'risk_amount': self.position_size.risk_amount,
            'risk_reward_ratio': self.position_size.risk_reward_ratio,
            'stop_loss_price': self.stop_loss.recommended_stop,
            'take_profit_1': self.take_profit.tp1_price,
            'take_profit_2': self.take_profit.tp2_price,
            'take_profit_3': self.take_profit.tp3_price,
            'is_valid': self.is_valid,
            'validation_errors': len(self.validation_errors),
            'validation_warnings': len(self.validation_warnings)
        }


@dataclass
class PortfolioRisk:
    """Portfolio-level risk assessment"""
    total_account_balance: float
    total_risk_amount: float
    total_risk_percentage: float
    
    # Position breakdown
    active_positions: int
    max_positions: int
    
    # Risk distribution
    risk_per_symbol: Dict[str, float]
    correlation_matrix: Dict[str, Dict[str, float]]
    
    # Risk limits
    daily_risk_limit: float
    weekly_risk_limit: float
    monthly_risk_limit: float
    
    # Risk status
    risk_level: RiskLevel
    can_take_new_position: bool
    recommended_position_size_multiplier: float
    
    timestamp: datetime