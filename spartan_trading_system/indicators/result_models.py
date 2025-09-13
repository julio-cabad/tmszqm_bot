"""
Result Models for Indicator Calculations
Standardized output formats for all indicators
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List


@dataclass
class TrendMagicResult:
    """Standardized result for Trend Magic indicator"""
    value: float
    color: str  # 'BLUE' or 'RED'
    trend_status: str
    trend_emoji: str
    distance_pct: float
    buy_signal: bool
    sell_signal: bool
    cci_value: float
    atr_value: float
    current_price: float
    timestamp: datetime
    version: str = "V3_TALIB"  # Using stable TA-Lib version


@dataclass
class SqueezeResult:
    """Standardized result for Squeeze Momentum indicator"""
    momentum_value: float
    momentum_color: str  # 'LIME', 'GREEN', 'RED', 'MAROON'
    momentum_trend: str
    squeeze_color: str  # 'BLUE', 'BLACK', 'GRAY'
    squeeze_status: str
    squeeze_on: bool
    squeeze_off: bool
    no_squeeze: bool
    bb_upper: float
    bb_lower: float
    kc_upper: float
    kc_lower: float
    current_price: float
    timestamp: datetime


@dataclass
class MultiTimeframeAnalysis:
    """Multi-timeframe analysis result"""
    symbol: str
    primary_timeframe: str
    confirmation_timeframe: str
    context_timeframe: str
    
    # Primary timeframe results
    primary_trend_magic: TrendMagicResult
    primary_squeeze: SqueezeResult
    
    # Confirmation timeframe results
    confirmation_trend_magic: TrendMagicResult
    confirmation_squeeze: SqueezeResult
    
    # Context timeframe results
    context_trend_magic: TrendMagicResult
    context_squeeze: SqueezeResult
    
    # Analysis summary
    overall_trend: str  # 'BULLISH', 'BEARISH', 'NEUTRAL'
    trend_strength: float  # 0.0 to 1.0
    timeframes_aligned: bool
    timestamp: datetime


@dataclass
class IndicatorSnapshot:
    """Complete indicator snapshot for a symbol"""
    symbol: str
    timeframe: str
    trend_magic: TrendMagicResult
    squeeze: SqueezeResult
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'timestamp': self.timestamp.isoformat(),
            'trend_magic': {
                'value': self.trend_magic.value,
                'color': self.trend_magic.color,
                'trend_status': self.trend_magic.trend_status,
                'distance_pct': self.trend_magic.distance_pct,
                'buy_signal': self.trend_magic.buy_signal,
                'sell_signal': self.trend_magic.sell_signal,
                'cci_value': self.trend_magic.cci_value,
                'version': self.trend_magic.version
            },
            'squeeze': {
                'momentum_value': self.squeeze.momentum_value,
                'momentum_color': self.squeeze.momentum_color,
                'momentum_trend': self.squeeze.momentum_trend,
                'squeeze_status': self.squeeze.squeeze_status,
                'squeeze_on': self.squeeze.squeeze_on,
                'squeeze_off': self.squeeze.squeeze_off,
                'no_squeeze': self.squeeze.no_squeeze
            }
        }