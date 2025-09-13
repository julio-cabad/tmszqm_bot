"""
Signal Types and Models for Spartan Trading System
Defines all signal classifications and trading signal structure
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional


class SignalType(Enum):
    """
    Spartan Signal Types - Based on Squeeze Magic Strategy
    """
    # SUPER SIGNALS - Highest Probability (85%+)
    SUPER_BULLISH = "super_bullish"           # Squeeze ON + Trend Magic BLUE + Momentum GREEN
    SUPER_BEARISH = "super_bearish"           # Squeeze ON + Trend Magic RED + Momentum RED
    
    # BREAKOUT SIGNALS - High Probability (75%+)
    BREAKOUT_BULLISH = "breakout_bullish"     # Squeeze OFF + Trend Magic BLUE + Momentum increasing
    BREAKOUT_BEARISH = "breakout_bearish"     # Squeeze OFF + Trend Magic RED + Momentum increasing
    
    # TREND CHANGE SIGNALS - Medium-High Probability (65%+)
    TREND_CHANGE_BULLISH = "trend_change_bullish"  # Trend Magic RED->BLUE + Momentum confirmation
    TREND_CHANGE_BEARISH = "trend_change_bearish"  # Trend Magic BLUE->RED + Momentum confirmation
    
    # CONTINUATION SIGNALS - Medium Probability (60%+)
    CONTINUATION_BULLISH = "continuation_bullish"  # Trend Magic BLUE + Momentum acceleration
    CONTINUATION_BEARISH = "continuation_bearish"  # Trend Magic RED + Momentum acceleration
    
    # SPECIAL SIGNALS
    SQUEEZE_COMPRESSION = "squeeze_compression"    # Squeeze turning ON (prepare for breakout)
    MOMENTUM_DIVERGENCE = "momentum_divergence"    # Price vs Momentum divergence
    
    # NO SIGNAL
    NO_SIGNAL = "no_signal"                       # Conditions not met or conflicting signals


class Direction(Enum):
    """Trading direction"""
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


class SignalStrength(Enum):
    """Signal strength classification"""
    VERY_STRONG = "very_strong"    # 0.85 - 1.0
    STRONG = "strong"              # 0.75 - 0.84
    MEDIUM = "medium"              # 0.60 - 0.74
    WEAK = "weak"                  # 0.40 - 0.59
    VERY_WEAK = "very_weak"        # 0.0 - 0.39


@dataclass
class TradingSignal:
    """
    Complete trading signal with all necessary information
    """
    # Basic Signal Info
    symbol: str
    timestamp: datetime
    signal_type: SignalType
    direction: Direction
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    
    # Price Information
    entry_price: float
    current_price: float
    
    # Risk Management
    stop_loss: float
    take_profit_levels: List[float]
    position_size_pct: float  # Percentage of account to risk
    
    # Technical Analysis Details
    trend_magic_value: float
    trend_magic_color: str
    squeeze_status: str
    momentum_color: str
    momentum_value: float
    
    # Multi-Timeframe Context
    timeframe: str
    context_timeframe_trend: str  # BULLISH, BEARISH, NEUTRAL
    confirmation_timeframe_trend: str
    timeframes_aligned: bool
    
    # Signal Generation Details
    trigger_reason: str  # Human readable explanation
    supporting_factors: List[str]  # List of supporting conditions
    risk_factors: List[str]  # List of risk factors
    
    # Metadata
    signal_id: Optional[str] = None
    created_by: str = "SpartanSignalGenerator"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary for storage/logging"""
        return {
            'signal_id': self.signal_id,
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'signal_type': self.signal_type.value,
            'direction': self.direction.value,
            'strength': self.strength,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'stop_loss': self.stop_loss,
            'take_profit_levels': self.take_profit_levels,
            'position_size_pct': self.position_size_pct,
            'trend_magic_value': self.trend_magic_value,
            'trend_magic_color': self.trend_magic_color,
            'squeeze_status': self.squeeze_status,
            'momentum_color': self.momentum_color,
            'momentum_value': self.momentum_value,
            'timeframe': self.timeframe,
            'context_timeframe_trend': self.context_timeframe_trend,
            'confirmation_timeframe_trend': self.confirmation_timeframe_trend,
            'timeframes_aligned': self.timeframes_aligned,
            'trigger_reason': self.trigger_reason,
            'supporting_factors': self.supporting_factors,
            'risk_factors': self.risk_factors,
            'created_by': self.created_by
        }
    
    def get_strength_classification(self) -> SignalStrength:
        """Get signal strength classification"""
        if self.strength >= 0.85:
            return SignalStrength.VERY_STRONG
        elif self.strength >= 0.75:
            return SignalStrength.STRONG
        elif self.strength >= 0.60:
            return SignalStrength.MEDIUM
        elif self.strength >= 0.40:
            return SignalStrength.WEAK
        else:
            return SignalStrength.VERY_WEAK
    
    def is_high_probability(self) -> bool:
        """Check if this is a high probability signal (75%+)"""
        return self.strength >= 0.75
    
    def is_super_signal(self) -> bool:
        """Check if this is a super signal (85%+)"""
        return self.signal_type in [SignalType.SUPER_BULLISH, SignalType.SUPER_BEARISH]
    
    def get_risk_reward_ratio(self) -> float:
        """Calculate risk/reward ratio"""
        if not self.take_profit_levels:
            return 0.0
        
        risk = abs(self.entry_price - self.stop_loss)
        if risk == 0:
            return 0.0
        
        # Use first take profit level for R:R calculation
        reward = abs(self.take_profit_levels[0] - self.entry_price)
        return reward / risk
    
    def __str__(self) -> str:
        """Human readable string representation"""
        strength_class = self.get_strength_classification().value.upper()
        rr_ratio = self.get_risk_reward_ratio()
        
        return (f"{self.signal_type.value.upper()} | {self.symbol} | "
                f"{self.direction.value.upper()} | {strength_class} "
                f"({self.strength:.2f}) | R:R {rr_ratio:.2f} | "
                f"{self.trigger_reason}")


@dataclass
class SignalContext:
    """
    Context information for signal generation
    Contains all the data needed to generate signals
    """
    symbol: str
    timeframe: str
    
    # Current indicator values
    trend_magic_current: Dict[str, Any]
    squeeze_current: Dict[str, Any]
    
    # Previous indicator values (for change detection)
    trend_magic_previous: Optional[Dict[str, Any]] = None
    squeeze_previous: Optional[Dict[str, Any]] = None
    
    # Multi-timeframe context
    context_timeframe_data: Optional[Dict[str, Any]] = None
    confirmation_timeframe_data: Optional[Dict[str, Any]] = None
    
    # Market data
    current_price: float = 0.0
    volume: float = 0.0
    
    # Timestamp
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# Signal Priority Mapping
SIGNAL_PRIORITY = {
    SignalType.SUPER_BULLISH: 10,
    SignalType.SUPER_BEARISH: 10,
    SignalType.BREAKOUT_BULLISH: 8,
    SignalType.BREAKOUT_BEARISH: 8,
    SignalType.TREND_CHANGE_BULLISH: 6,
    SignalType.TREND_CHANGE_BEARISH: 6,
    SignalType.CONTINUATION_BULLISH: 4,
    SignalType.CONTINUATION_BEARISH: 4,
    SignalType.SQUEEZE_COMPRESSION: 3,
    SignalType.MOMENTUM_DIVERGENCE: 2,
    SignalType.NO_SIGNAL: 0
}

# Expected Win Rates by Signal Type
SIGNAL_WIN_RATES = {
    SignalType.SUPER_BULLISH: 0.85,
    SignalType.SUPER_BEARISH: 0.85,
    SignalType.BREAKOUT_BULLISH: 0.75,
    SignalType.BREAKOUT_BEARISH: 0.75,
    SignalType.TREND_CHANGE_BULLISH: 0.65,
    SignalType.TREND_CHANGE_BEARISH: 0.65,
    SignalType.CONTINUATION_BULLISH: 0.60,
    SignalType.CONTINUATION_BEARISH: 0.60,
    SignalType.SQUEEZE_COMPRESSION: 0.50,
    SignalType.MOMENTUM_DIVERGENCE: 0.55,
    SignalType.NO_SIGNAL: 0.0
}