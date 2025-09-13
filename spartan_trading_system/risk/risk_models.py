"""
Risk Management Models
Data structures for risk calculations and portfolio management
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class RiskLevel(Enum):
    """Risk level classification"""
    VERY_LOW = "very_low"      # < 1%
    LOW = "low"                # 1-2%
    MEDIUM = "medium"          # 2-3%
    HIGH = "high"              # 3-5%
    VERY_HIGH = "very_high"    # > 5%


class PositionType(Enum):
    """Position type"""
    LONG = "long"
    SHORT = "short"


@dataclass
class RiskParameters:
    """
    Risk parameters for position calculation
    """
    # Account settings
    account_balance: float
    max_risk_per_trade: float  # Percentage (e.g., 2.0 for 2%)
    max_portfolio_risk: float  # Percentage (e.g., 10.0 for 10%)
    
    # Position limits
    max_positions: int
    max_positions_per_symbol: int
    
    # Risk multipliers based on signal strength
    risk_multiplier_very_strong: float = 1.5  # 150% of base risk for very strong signals
    risk_multiplier_strong: float = 1.2       # 120% of base risk for strong signals
    risk_multiplier_medium: float = 1.0       # 100% of base risk for medium signals
    risk_multiplier_weak: float = 0.7         # 70% of base risk for weak signals
    risk_multiplier_very_weak: float = 0.5    # 50% of base risk for very weak signals
    
    # Stop loss settings
    min_stop_loss_distance: float = 0.005     # Minimum 0.5% stop loss
    max_stop_loss_distance: float = 0.05      # Maximum 5% stop loss
    
    # Take profit settings
    default_risk_reward_ratios: List[float] = None
    
    def __post_init__(self):
        if self.default_risk_reward_ratios is None:
            self.default_risk_reward_ratios = [1.5, 2.5, 4.0]  # Multiple TP levels
    
    def get_risk_multiplier(self, signal_strength: float) -> float:
        """Get risk multiplier based on signal strength"""
        if signal_strength >= 0.85:
            return self.risk_multiplier_very_strong
        elif signal_strength >= 0.75:
            return self.risk_multiplier_strong
        elif signal_strength >= 0.60:
            return self.risk_multiplier_medium
        elif signal_strength >= 0.40:
            return self.risk_multiplier_weak
        else:
            return self.risk_multiplier_very_weak
    
    def classify_risk_level(self, risk_percentage: float) -> RiskLevel:
        """Classify risk level based on percentage"""
        if risk_percentage < 1.0:
            return RiskLevel.VERY_LOW
        elif risk_percentage < 2.0:
            return RiskLevel.LOW
        elif risk_percentage < 3.0:
            return RiskLevel.MEDIUM
        elif risk_percentage < 5.0:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH


@dataclass
class PositionRisk:
    """
    Risk calculation result for a single position
    """
    symbol: str
    position_type: PositionType
    
    # Price levels
    entry_price: float
    stop_loss: float
    take_profit_levels: List[float]
    
    # Position sizing
    position_size_usd: float
    position_size_percentage: float
    position_size_units: float  # Number of units/coins
    
    # Risk metrics
    risk_amount_usd: float
    risk_percentage: float
    risk_level: RiskLevel
    
    # Reward metrics
    potential_rewards_usd: List[float]  # For each TP level
    risk_reward_ratios: List[float]     # For each TP level
    
    # Signal context
    signal_strength: float
    signal_type: str
    
    # Validation
    is_valid: bool
    validation_errors: List[str]
    
    # Metadata
    calculated_at: datetime
    
    def get_best_risk_reward(self) -> float:
        """Get the best risk/reward ratio"""
        return max(self.risk_reward_ratios) if self.risk_reward_ratios else 0.0
    
    def get_total_potential_reward(self) -> float:
        """Get total potential reward if all TPs hit"""
        return sum(self.potential_rewards_usd) if self.potential_rewards_usd else 0.0
    
    def is_acceptable_risk(self) -> bool:
        """Check if risk is acceptable"""
        return (self.is_valid and 
                self.risk_level in [RiskLevel.VERY_LOW, RiskLevel.LOW, RiskLevel.MEDIUM] and
                len(self.validation_errors) == 0)


@dataclass
class PortfolioRisk:
    """
    Portfolio-level risk analysis
    """
    # Current portfolio state
    total_account_balance: float
    current_positions: List[PositionRisk]
    
    # Risk metrics
    total_risk_usd: float
    total_risk_percentage: float
    available_risk_usd: float
    available_risk_percentage: float
    
    # Position metrics
    active_positions_count: int
    max_positions: int
    positions_by_symbol: Dict[str, int]
    
    # Correlation analysis
    symbol_correlation_risk: float  # Risk from correlated positions
    
    # Portfolio limits
    portfolio_risk_level: RiskLevel
    can_add_position: bool
    max_new_position_size: float
    
    # Warnings and recommendations
    risk_warnings: List[str]
    recommendations: List[str]
    
    # Metadata
    calculated_at: datetime
    
    def get_risk_utilization(self) -> float:
        """Get percentage of total risk capacity being used"""
        max_portfolio_risk = 10.0  # 10% max portfolio risk
        return (self.total_risk_percentage / max_portfolio_risk) * 100
    
    def is_overexposed(self) -> bool:
        """Check if portfolio is overexposed to risk"""
        return (self.total_risk_percentage > 8.0 or  # More than 8% total risk
                self.get_risk_utilization() > 80)    # More than 80% risk utilization
    
    def get_diversification_score(self) -> float:
        """Calculate diversification score (0-1, higher is better)"""
        if not self.current_positions:
            return 1.0
        
        # Simple diversification based on number of different symbols
        unique_symbols = len(set(pos.symbol for pos in self.current_positions))
        max_diversification = min(len(self.current_positions), 10)  # Max 10 for perfect diversification
        
        return unique_symbols / max_diversification if max_diversification > 0 else 0.0


@dataclass
class RiskValidationResult:
    """
    Result of risk validation checks
    """
    is_valid: bool
    risk_level: RiskLevel
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]
    
    # Specific validations
    position_size_valid: bool
    stop_loss_valid: bool
    portfolio_risk_valid: bool
    correlation_risk_valid: bool
    
    # Calculated metrics
    final_position_size: float
    adjusted_stop_loss: float
    expected_risk_reward: float
    
    def has_blocking_errors(self) -> bool:
        """Check if there are errors that block position opening"""
        return not self.is_valid or len(self.errors) > 0
    
    def get_risk_summary(self) -> str:
        """Get human-readable risk summary"""
        status = "APPROVED" if self.is_valid else "REJECTED"
        return f"{status} | {self.risk_level.value.upper()} | ${self.final_position_size:,.2f} | R:R {self.expected_risk_reward:.2f}"